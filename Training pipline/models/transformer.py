import tensorflow as tf


def build_transformer(input_shape: tuple, num_heads: int = 4, key_dim: int = 64, ff_dim: int = 32) -> tf.keras.Model:
    """
    This function takes in the input shape and number of filters for the transformer layer,
    and returns a compiled transformer model.
    Parameters:
    input_shape (tuple): A tuple containing the shape of the input data.
    num_heads (int): The number of attention heads. Default is 4.
    key_dim (int): The dimension of the key and value vectors. Default is 64.
    ff_dim (int): The dimension of the feed-forward layer. Default is 32.
    Returns:
    tf.keras.Model: A compiled transformer model.
    """
    timesteps, features = input_shape
    inputs = tf.keras.Input(shape=input_shape)

    # Learnable positional encoding
    positions = tf.range(start=0, limit=timesteps, delta=1)
    pos_embedding = tf.keras.layers.Embedding(
        input_dim=timesteps, output_dim=features)(positions)
    x = inputs + pos_embedding

    attn_output = tf.keras.layers.MultiHeadAttention(
        num_heads=num_heads, key_dim=key_dim)(x, x)
    attn_output = tf.keras.layers.Dropout(0.2)(attn_output)
    x1 = tf.keras.layers.LayerNormalization()(attn_output + x)
    ff_output = tf.keras.layers.Dense(ff_dim, activation='relu')(x1)
    ff_output = tf.keras.layers.Dense(features)(ff_output)
    ff_output = tf.keras.layers.Dropout(0.2)(ff_output)
    x2 = tf.keras.layers.LayerNormalization()(ff_output + x1)
    x3 = tf.keras.layers.GlobalAveragePooling1D()(x2)
    output = tf.keras.layers.Dense(units=1, activation='linear')(x3)
    model = tf.keras.Model(inputs, output)

    model.compile(optimizer='adam', loss='mse')

    return model
