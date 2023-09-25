import * as tf from '@tensorflow/tfjs';

const MOBILE_NET_INPUT_WIDTH = 224;
const MOBILE_NET_INPUT_HEIGHT = 224;

export async function loadMobileNetFeatureModel() {
	const URL =
		'https://tfhub.dev/google/tfjs-model/imagenet/mobilenet_v3_small_100_224/feature_vector/5/default/1';
	const mobilenet = await tf.loadGraphModel(URL, { fromTFHub: true });
	console.log('MobileNet v3 loaded successfully!');
	// Warm up the model by passing zeros through it once.
	tf.tidy(function () {
		const answer = mobilenet.predict(
			tf.zeros([1, MOBILE_NET_INPUT_HEIGHT, MOBILE_NET_INPUT_WIDTH, 3])
		) as tf.Tensor<tf.Rank>;
    console.log(answer.shape);
  });
  return mobilenet;
}

export async function defineModelHead() {

  const model = tf.sequential();
  model.add(tf.layers.dense({ inputShape: [1024], units: 128, activation: 'relu' }));
  model.add(tf.layers.dense({ units: 1, activation: 'softmax' }));

  model.summary();

  model.compile({
    // Adam changes the learning rate over time which is useful.
    optimizer: 'adam',
    // Use the correct loss function. If 2 classes of data, must use binaryCrossentropy.
    // Else categoricalCrossentropy is used if more than 2 classes.
    // loss: NUMBER_OF_CHANNELS === 2 ? 'binaryCrossentropy' : 'categoricalCrossentropy',
    loss: 'categoricalCrossentropy',
    // As this is a classification problem you can record accuracy in the logs too!
    metrics: ['accuracy']
  });

  return model;
}


