import tensorflow as tf


def build_lstm(input_shape: tuple, units: int = 64) -> tf.keras.Model:
    """
    This function takes in the input shape and number of units for the LSTM layer, 
    and returns a compiled LSTM model.
    Parameters:
    input_shape (tuple): A tuple containing the shape of the input data.
    units (int): The number of units for the LSTM layer. Default is 64.
    Returns:
    tf.keras.Model: A compiled LSTM model.
    """

    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(
            units=units, input_shape=input_shape, return_sequences=True),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(units=units),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(units=1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse')

    return model
