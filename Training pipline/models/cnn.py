import tensorflow as tf


def build_cnn(input_shape: tuple, filters: int = 64) -> tf.keras.Model:
    """
    This function takes in the input shape and number of filters for the CNN layer, 
    and returns a compiled CNN model.
    Parameters:
    input_shape (tuple): A tuple containing the shape of the input data.
    filters (int): The size of the filters for the CNN layer. Default is 64.
    Returns:
    tf.keras.Model: A compiled CNN (conv1d) model.
    """

    model = tf.keras.Sequential([
        tf.keras.layers.Conv1D(
            filters=filters, input_shape=input_shape, kernel_size=3,
            padding='same', activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Conv1D(
            filters=filters//2, kernel_size=3,
            padding='same', activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(units=1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse')

    return model
