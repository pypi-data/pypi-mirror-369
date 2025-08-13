# tests/test_basic.py
import numpy as np
import pytest
from sklearn.datasets import load_iris, make_regression, make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.svm import SVC
from sheshe import ModalBoundaryClustering

def test_import_and_fit():
    iris = load_iris()
    X, y = iris.data, iris.target
    sh = ModalBoundaryClustering(base_estimator=LogisticRegression(max_iter=200), task="classification", random_state=0)
    sh.fit(X, y)
    y_hat = sh.predict(X)
    assert y_hat.shape[0] == X.shape[0]
    proba = sh.predict_proba(X[:3])
    assert proba.shape[0] == 3
    df = sh.interpretability_summary(iris.feature_names)
    assert {"Tipo","Distancia","Categoria"}.issubset(df.columns)
    score = sh.score(X, y)
    assert 0.0 <= score <= 1.0


def test_score_regression():
    X, y = make_regression(n_samples=100, n_features=4, noise=0.1, random_state=0)
    sh = ModalBoundaryClustering(
        base_estimator=RandomForestRegressor(n_estimators=10, random_state=0),
        task="regression",
        random_state=0,
    )
    sh.fit(X, y)
    score = sh.score(X, y)
    assert np.isfinite(score)


def test_predict_regression_returns_base_estimator_value():
    X, y = make_regression(n_samples=80, n_features=5, noise=0.1, random_state=0)
    sh = ModalBoundaryClustering(
        base_estimator=RandomForestRegressor(n_estimators=10, random_state=0),
        task="regression",
        random_state=0,
    )
    sh.fit(X, y)
    expected = sh.pipeline_.predict(X[:5])
    y_hat = sh.predict(X[:5])
    assert np.allclose(y_hat, expected)


def test_decision_function_classifier_and_fallback():
    iris = load_iris()
    X, y = iris.data, iris.target
    # Estimador con decision_function
    sh = ModalBoundaryClustering(
        base_estimator=LogisticRegression(max_iter=200),
        task="classification",
        random_state=0,
    )
    sh.fit(X, y)
    Xs = sh.scaler_.transform(X[:5])
    expected = sh.estimator_.decision_function(Xs)
    df_scores = sh.decision_function(X[:5])
    assert np.allclose(df_scores, expected)

    # Estimador sin decision_function → usa predict_proba
    sh2 = ModalBoundaryClustering(
        base_estimator=RandomForestClassifier(n_estimators=10, random_state=0),
        task="classification",
        random_state=0,
    )
    sh2.fit(X, y)
    Xs2 = sh2.scaler_.transform(X[:5])
    expected2 = sh2.estimator_.predict_proba(Xs2)
    df_scores2 = sh2.decision_function(X[:5])
    assert np.allclose(df_scores2, expected2)


def test_decision_function_regression_fallback():
    X, y = make_regression(n_samples=50, n_features=4, noise=0.1, random_state=0)
    sh = ModalBoundaryClustering(
        base_estimator=RandomForestRegressor(n_estimators=5, random_state=0),
        task="regression",
        random_state=0,
    )
    sh.fit(X, y)
    Xs = sh.scaler_.transform(X[:5])
    expected = sh.estimator_.predict(Xs)
    df_scores = sh.decision_function(X[:5])
    assert np.allclose(df_scores, expected)


def test_predict_proba_and_value_without_predict_proba():
    X, y = make_classification(n_samples=40, n_features=5, random_state=0)
    sh = ModalBoundaryClustering(
        base_estimator=SVC(kernel="linear"),
        task="classification",
        random_state=0,
    )
    sh.fit(X, y)
    Xs = sh.scaler_.transform(X[:5])
    scores = sh.estimator_.decision_function(Xs)
    proba = sh.predict_proba(X[:5])
    expected = np.column_stack([-scores.reshape(-1, 1), scores.reshape(-1, 1)])
    assert np.allclose(proba, expected)
    val1 = sh._predict_value_real(X[:5], class_idx=1)
    val0 = sh._predict_value_real(X[:5], class_idx=0)
    assert np.allclose(val1, scores)
    assert np.allclose(val0, -scores)


def test_scan_steps_minimum():
    with pytest.raises(ValueError):
        ModalBoundaryClustering(scan_steps=1)


def test_membership_matrix_no_directions():
    iris = load_iris()
    X, y = iris.data[:, :2], iris.target
    sh = ModalBoundaryClustering(
        base_estimator=LogisticRegression(max_iter=200),
        task="classification",
        base_2d_rays=0,
        random_state=0,
    )
    sh.fit(X, y)
    M = sh._membership_matrix(X)
    assert M.shape == (X.shape[0], len(sh.regions_))
    assert np.all(M == 0)
    base_pred = sh.pipeline_.predict(X)
    pred = sh.predict(X)
    assert np.all(pred == base_pred)


def test_base_2d_rays_zero_raises_in_3d():
    iris = load_iris()
    X, y = iris.data[:, :3], iris.target
    sh = ModalBoundaryClustering(
        base_estimator=LogisticRegression(max_iter=200),
        task="classification",
        base_2d_rays=0,
        random_state=0,
    )
    with pytest.raises(ValueError, match="base_2d"):
        sh.fit(X, y)


def test_n_max_seeds_minimum():
    with pytest.raises(ValueError, match="n_max_seeds"):
        ModalBoundaryClustering(n_max_seeds=0)


def test_fit_raises_when_y_none_classification():
    X = np.random.randn(10, 3)
    sh = ModalBoundaryClustering(task="classification")
    with pytest.raises(ValueError, match="y cannot be None"):
        sh.fit(X, None)


def test_fit_raises_with_single_class():
    X = np.random.randn(10, 3)
    y = np.zeros(10)
    sh = ModalBoundaryClustering(task="classification")
    with pytest.raises(ValueError, match="at least two classes"):
        sh.fit(X, y)
