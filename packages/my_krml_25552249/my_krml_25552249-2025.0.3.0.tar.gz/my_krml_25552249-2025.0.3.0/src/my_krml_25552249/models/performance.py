def print_regressor_scores(y_preds, y_actuals, set_name=None):
    """Print the RMSE and MAE for the provided data

    Parameters
    ----------
    y_preds : Numpy Array
        Predicted target
    y_actuals : Numpy Array
        Actual target
    set_name : str
        Name of the set to be printed

    Returns
    -------
    """
    from sklearn.metrics import root_mean_squared_error as rmse
    from sklearn.metrics import mean_absolute_error as mae

    print(f"RMSE {set_name}: {rmse(y_actuals, y_preds)}")
    print(f"MAE {set_name}: {mae(y_actuals, y_preds)}")


def print_aucroc_score(y_preds, y_actuals, set_name=None):
    """Print the AUC-ROC score for the provided data

    Parameters
    ----------
    y_preds : Numpy Array or list
        Predicted probabilities or scores for the positive class
    y_actuals : Numpy Array or list
        Actual binary target labels (0 or 1)
    set_name : str
        Name of the set to be printed

    Returns
    -------
    """
    from sklearn.metrics import roc_auc_score

    aucroc = roc_auc_score(y_actuals, y_preds)
    print(f"AUC-ROC {set_name}: {aucroc}")



def plot_confusion_matrix(model, X, y, title="Confusion Matrix"):
    """
    Fits the model (if not already fitted) and plots the confusion matrix for given X, y.
    
    Parameters:
    model: Fitted classifier with a .predict() method
    X: Features
    y: True labels
    title: Title for the confusion matrix
    """
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
    import matplotlib.pyplot as plt

    y_pred = model.predict(X)
    cm = confusion_matrix(y, y_pred)
    
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(values_format='d', cmap='Blues')
    plt.title(title)
    plt.show()

