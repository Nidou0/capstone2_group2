import tensorflow as tf
from config import EPOCHS, BATCH_SIZE, PATIENCE, EARLY_STOPPING_ROUNDS


def train_model(model: tf.keras.Model, X_train, y_train, X_val, y_val, epochs: int = EPOCHS, batch_size: int = BATCH_SIZE, patience: int = PATIENCE) -> tuple[tf.keras.Model, tf.keras.callbacks.History]:
    """
    This function takes in a compiled model, training and validation data, and training parameters.
    It trains the model using early stopping and learning rate reduction on plateau, and returns the trained
    model and the training history.
    Parameters:
    model (tf.keras.Model): A compiled Keras model to be trained.
    X_train (np.ndarray): A numpy array containing the training features.
    y_train (np.ndarray): A numpy array containing the training target variable.
    X_val (np.ndarray): A numpy array containing the validation features.
    y_val (np.ndarray): A numpy array containing the validation target variable.
    epochs (int): The number of epochs to train the model. Default is 100.
    batch_size (int): The batch size to use during training. Default is 32.
    patience (int): The number of epochs with no improvement after which training will be stopped. Default is 10.
    Returns:
    tuple: A tuple containing the trained model and the training history.
    """
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=patience,
        restore_best_weights=True
    )

    # ReduceLR callback
    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        patience=5,  # triggers before early stopping
        factor=0.5   # halves the learning rate
    )

    history = model.fit(x=X_train, y=y_train, epochs=epochs, batch_size=batch_size,
                        validation_data=(X_val, y_val), callbacks=[early_stopping, reduce_lr])

    return model, history


def boost_train_model(model, X_train, y_train, X_val, y_val):

    history = model.fit(X_train, y_train, eval_set=[
                        (X_val, y_val)])
    return model, history


def rf_train_model(model, X_train, y_train, X_val, y_val):

    model.fit(X_train, y_train)
    return model, None
