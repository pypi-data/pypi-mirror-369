# vacancy_keras.py
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix
import joblib

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import warnings

# ----------------------------
# Configuración del modelo
# ----------------------------
@dataclass
class ModelConfig:
    # Datos
    target_col: str = "vacancys"
    test_size: float = 0.25
    val_size_of_tmp: float = 0.5         # proporción de (train_test_split tmp) que va a test
    random_state: int = 42
    # Red
    hidden_units: Tuple[int, int, int] = (256, 128, 64)
    dropout: float = 0.25
    learning_rate: float = 1e-3
    # Entrenamiento
    batch_size: int = 64
    epochs: int = 300
    early_stopping_patience: int = 20
    reduce_lr_patience: int = 8
    class_weight_balanced: bool = True
    # Paths artefactos
    artifacts_dir: Union[str, Path] = "artifacts_keras"
    best_model_name: str = "best_model.keras"
    last_model_name: str = "last_model.keras"
    scaler_name: str = "scaler_vacancies.pkl"
    feature_order_name: str = "feature_order.json"
    config_dump_name: str = "config_used.json"
    # Métricas
    monitor_metric: str = "val_accuracy"
    topk: int = 3


# ---------------------------------
# Clasificador Keras OOP
# ---------------------------------
class VacancyClassifierKeras:
    def __init__(self, config: Optional[ModelConfig] = None):
        self.cfg = config or ModelConfig()
        self.model: Optional[keras.Model] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_order: List[str] = []
        self.num_classes: Optional[int] = None

        self.artifacts_dir = Path(self.cfg.artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    # ---------- Carga de datos ----------
    def load_json(self, path: Union[str, Path]) -> pd.DataFrame:
        path = Path(path)
        with path.open("r") as f:
            data = json.load(f)
        df = pd.DataFrame(data).dropna().reset_index(drop=True)
        if self.cfg.target_col not in df.columns:
            raise ValueError(f"No se encontró la columna objetivo '{self.cfg.target_col}' en {path}.")
        return df

    # ---------- Preparación ----------
    def prepare_arrays(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        self.feature_order = [c for c in df.columns if c != self.cfg.target_col]
        X = df[self.feature_order].astype("float32").values
        y_raw = df[self.cfg.target_col].astype("int32").values
        # A Keras le pasamos 0..C-1
        y = y_raw - 1
        self.num_classes = int(y.max() + 1)
        return X, y

    def split_and_scale(
        self, X: np.ndarray, y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        import numpy as np

        rng = self.cfg.random_state
        test_size = self.cfg.test_size
        val_size  = self.cfg.val_size_of_tmp

        y = np.asarray(y)

        # --- helper: ¿se puede estratificar? (>=2 clases y todas con >=2 muestras)
        def can_stratify(labels: np.ndarray) -> bool:
            u, c = np.unique(labels, return_counts=True)
            return (len(u) >= 2) and (c.min() >= 2)

        # --- Split 1: train / tmp (estratificar solo si se puede)
        strat_full = y if can_stratify(y) else None
        if strat_full is None:
            print("[KERAS] ⚠️ Estratificación DESACTIVADA en train/tmp.")
        X_train, X_tmp, y_train, y_tmp = train_test_split(
            X, y, test_size=test_size, random_state=rng, stratify=strat_full
        )

        # --- Split 2: val / test (estratificar solo si se puede)
        strat_tmp = y_tmp if can_stratify(y_tmp) else None
        if strat_tmp is None:
            print("[KERAS] ⚠️ Estratificación DESACTIVADA en val/test.")
        X_val, X_test, y_val, y_test = train_test_split(
            X_tmp, y_tmp, test_size=val_size, random_state=rng, stratify=strat_tmp
        )

        # --- Garantizar que TRAIN vea todas las clases (si no, reintentar sin stratify)
        all_cls   = set(np.unique(y))
        train_cls = set(np.unique(y_train))
        if train_cls != all_cls:
            print("[KERAS] ⚠️ TRAIN no contiene todas las clases. Reintentando SIN stratify...")
            X_train, X_tmp, y_train, y_tmp = train_test_split(
                X, y, test_size=test_size, random_state=rng + 1, stratify=None
            )
            X_val, X_test, y_val, y_test = train_test_split(
                X_tmp, y_tmp, test_size=val_size, random_state=rng + 1, stratify=None
            )

        # --- Escalado (al final, sobre el split definitivo)
        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(X_train)
        X_val   = self.scaler.transform(X_val)
        X_test  = self.scaler.transform(X_test)

        # Debug útil
        print("[KERAS] split OK | train/val/test =", X_train.shape, X_val.shape, X_test.shape)
        print("[KERAS] clases train:", dict(zip(*np.unique(y_train, return_counts=True))))
        print("[KERAS] clases  val :", dict(zip(*np.unique(y_val,   return_counts=True))))
        print("[KERAS] clases test:", dict(zip(*np.unique(y_test,  return_counts=True))))

        return X_train, X_val, X_test, y_train, y_val, y_test


    # ---------- Modelo ----------
    def build_model(self, input_dim: int) -> keras.Model:
        if self.num_classes is None:
            raise RuntimeError("num_classes no definido. Ejecuta prepare_arrays primero.")
        units1, units2, units3 = self.cfg.hidden_units

        inputs = keras.Input(shape=(input_dim,))
        x = layers.Dense(units1, activation=None)(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.Dropout(self.cfg.dropout)(x)

        x = layers.Dense(units2, activation=None)(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.Dropout(self.cfg.dropout)(x)

        x = layers.Dense(units3, activation="relu")(x)
        outputs = layers.Dense(self.num_classes, activation="softmax")(x)
        model = keras.Model(inputs, outputs)

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.cfg.learning_rate),
            loss="sparse_categorical_crossentropy",
            metrics=[
                "accuracy",
                keras.metrics.SparseTopKCategoricalAccuracy(k=self.cfg.topk, name=f"top{self.cfg.topk}_acc"),
            ],
        )
        self.model = model
        return model

# Agregar dentro de vacancy_keras.py, en la clase VacancyClassifierKeras



    def _check_and_build_matrix_from_df(self, df: pd.DataFrame) -> np.ndarray:
        """
        Verifica que el DataFrame tenga las columnas necesarias en self.feature_order.
        Ignora columnas extra; si faltan columnas requeridas, lanza error.
        """
        if not self.feature_order:
            raise RuntimeError(
                "feature_order vacío. Entrená el modelo o cargá artefactos con load_artifacts() primero."
            )

        missing = [c for c in self.feature_order if c not in df.columns]
        if missing:
            raise ValueError(
                f"Faltan columnas en el CSV para predecir: {missing}. "
                f"Se esperaban exactamente estas features: {self.feature_order}"
            )

        # Advertencia si hay columnas extra (serán ignoradas)
        extras = [c for c in df.columns if c not in self.feature_order]
        if extras:
            warnings.warn(f"Columnas extra ignoradas al predecir: {extras}", UserWarning)

        X = df[self.feature_order].astype("float32").values
        return X

    def predict_dataframe(self, df: pd.DataFrame, return_probs: bool = True) -> pd.DataFrame:
        """
        Recibe un DataFrame con al menos las columnas de self.feature_order.
        Devuelve un DataFrame con columnas nuevas:
        - pred_vacancys (clase 1..C)
        - (opcional) prob_1, prob_2, ..., prob_C
        """
        if self.model is None or self.scaler is None:
            raise RuntimeError("Modelo/escalador no cargados. Usá load_artifacts() o entrená el modelo.")

        X = self._check_and_build_matrix_from_df(df)
        Xs = self.scaler.transform(X)
        probs = self.model.predict(Xs, verbose=0)
        preds_0 = np.argmax(probs, axis=1)
        preds_1 = preds_0 + 1  # pasar a 1..C

        out = df.copy()
        out["pred_vacancys"] = preds_1.astype(int)

        if return_probs:
            # num_classes de la salida del modelo
            C = probs.shape[1]
            for k in range(C):
                out[f"prob_{k+1}"] = probs[:, k].astype(float)

        return out

    def predict_csv(
        self,
        input_csv: Union[str, Path],
        output_csv: Optional[Union[str, Path]] = None,
        return_probs: bool = True,
        float_fmt: str = "%.6f",
    ) -> pd.DataFrame:
        """
        Lee un CSV, predice por fila y guarda un nuevo CSV con predicciones.
        - input_csv: ruta al CSV de entrada.
        - output_csv: si se da, guarda el CSV con columnas nuevas.
        - return_probs: añade columnas prob_i por clase.
        """
        input_csv = Path(input_csv)
        if not input_csv.exists():
            raise FileNotFoundError(input_csv)

        df_in = pd.read_csv(input_csv)
        df_out = self.predict_dataframe(df_in, return_probs=return_probs)

        if output_csv is not None:
            output_csv = Path(output_csv)
            output_csv.parent.mkdir(parents=True, exist_ok=True)
            df_out.to_csv(output_csv, index=False, float_format=float_fmt)

        return df_out


    # ---------- Callbacks ----------
    def _callbacks(self) -> List[keras.callbacks.Callback]:
        return [
            keras.callbacks.EarlyStopping(
                monitor=self.cfg.monitor_metric, patience=self.cfg.early_stopping_patience, restore_best_weights=True
            ),
            keras.callbacks.ModelCheckpoint(
                filepath=str(self.artifacts_dir / self.cfg.best_model_name),
                monitor=self.cfg.monitor_metric,
                save_best_only=True,
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=self.cfg.reduce_lr_patience, min_lr=1e-6
            ),
        ]

    # ---------- Pesos de clase ----------
    def _class_weights(self, y_train: np.ndarray) -> Optional[Dict[int, float]]:
        if not self.cfg.class_weight_balanced:
            return None
        classes = np.arange(int(y_train.max() + 1))
        w = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
        return {int(c): float(wi) for c, wi in zip(classes, w)}

    # ---------- Entrenamiento ----------
    def fit(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        verbose: int = 1,
    ) -> keras.callbacks.History:
        if self.model is None:
            self.build_model(input_dim=X_train.shape[1])
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.cfg.epochs,
            batch_size=self.cfg.batch_size,
            class_weight=self._class_weights(y_train),
            verbose=verbose,
            callbacks=self._callbacks(),
        )
        # Guardar último estado además del mejor checkpoint
        self.model.save(self.artifacts_dir / self.cfg.last_model_name)
        # Persistir scaler, orden de features y config usada
        joblib.dump(self.scaler, self.artifacts_dir / self.cfg.scaler_name)
        (self.artifacts_dir / self.cfg.feature_order_name).write_text(json.dumps(self.feature_order))
        (self.artifacts_dir / self.cfg.config_dump_name).write_text(json.dumps(asdict(self.cfg), indent=2))
        return history

    # ---------- Evaluación ----------
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        if self.model is None:
            raise RuntimeError("No hay modelo cargado/entrenado.")
        metrics_values = self.model.evaluate(X_test, y_test, verbose=0)
        result = {name: float(val) for name, val in zip(self.model.metrics_names, metrics_values)}
        y_prob = self.model.predict(X_test, verbose=0)
        y_pred = np.argmax(y_prob, axis=1)

        print("\n== Evaluación detallada (clases 1..C) ==")
        print(classification_report(y_test + 1, y_pred + 1, digits=3))
        print("Matriz de confusión:")
        print(confusion_matrix(y_test + 1, y_pred + 1))
        return result

    # ---------- Carga de artefactos ----------
    def load_artifacts(
        self,
        best: bool = True,
    ) -> None:
        model_path = self.artifacts_dir / (self.cfg.best_model_name if best else self.cfg.last_model_name)
        scaler_path = self.artifacts_dir / self.cfg.scaler_name
        feature_path = self.artifacts_dir / self.cfg.feature_order_name

        self.model = keras.models.load_model(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_order = json.loads(feature_path.read_text())
        # num_classes implícito
        self.num_classes = self.model.output_shape[-1]

    # ---------- Inferencia ----------
    def _to_row(self, features: Dict[str, float]) -> np.ndarray:
        if not self.feature_order:
            raise RuntimeError("feature_order vacío: cargá artefactos o entrená primero.")
        return np.array([[features[c] for c in self.feature_order]], dtype="float32")

    def predict_one(self, features: Dict[str, float]) -> Tuple[int, Dict[int, float]]:
        if self.model is None or self.scaler is None:
            raise RuntimeError("Modelo/escalador no cargados. Usá load_artifacts() o entrená el modelo.")
        x = self._to_row(features)
        x = self.scaler.transform(x)
        probs = self.model.predict(x, verbose=0)[0]
        pred_0 = int(np.argmax(probs))
        pred_1 = pred_0 + 1
        probs_dict = {int(i + 1): float(p) for i, p in enumerate(probs)}
        return pred_1, probs_dict

    def predict_batch(self, features_list: List[Dict[str, float]]) -> List[Tuple[int, Dict[int, float]]]:
        if self.model is None or self.scaler is None:
            raise RuntimeError("Modelo/escalador no cargados. Usá load_artifacts() o entrená el modelo.")
        X = np.array([[f[c] for c in self.feature_order] for f in features_list], dtype="float32")
        Xs = self.scaler.transform(X)
        probs = self.model.predict(Xs, verbose=0)
        preds_0 = np.argmax(probs, axis=1)
        results = []
        for i, p in enumerate(probs):
            pred_1 = int(preds_0[i] + 1)
            probs_dict = {int(k + 1): float(v) for k, v in enumerate(p)}
            results.append((pred_1, probs_dict))
        return results


