<script lang="ts">
	import * as tf from '@tensorflow/tfjs';
	import ImageGrid from './ImageGrid.svelte';

	const MOBILE_NET_INPUT_WIDTH = 224;
	const MOBILE_NET_INPUT_HEIGHT = 224;
	let trainingFileList:
		| {
				file: File;
				uuid: string;
		  }[]
		| null = null;
	let collectionFileList: FileList | null = null;
	let mobileNet: tf.GraphModel | null = null;
	let model: tf.Sequential | null = null;

	async function loadMobileNetFeatureModel() {
		const URL =
			'https://tfhub.dev/google/tfjs-model/imagenet/mobilenet_v3_small_100_224/feature_vector/5/default/1';
		mobileNet = await tf.loadGraphModel(URL, { fromTFHub: true });
		console.log('MobileNet v3 loaded successfully!');
		// Warm up the model by passing zeros through it once.

		tf.tidy(function () {
			const answer = mobileNet?.predict(
				tf.zeros([1, MOBILE_NET_INPUT_HEIGHT, MOBILE_NET_INPUT_WIDTH, 3])
			) as tf.Tensor<tf.Rank>;
			console.log(answer.shape);
		});
	}

	function loadCustomModel() {
		model = tf.sequential();
		model.add(tf.layers.dense({ inputShape: [1024], units: 128, activation: 'relu' }));
		model.add(tf.layers.dense({ units: 1, activation: 'softmax' }));

		model.summary();

		model.compile({
			// Adam changes the learning rate over time which is useful.
			optimizer: 'adam',
			// Use the correct loss function. If 2 classes of data, must use binaryCrossentropy.
			// Else categoricalCrossentropy is used if more than 2 classes.
			// loss: NUMBER_OF_CHANNELS === 2 ? 'binaryCrossentropy' : 'categoricalCrossentropy',
			loss: 'binaryCrossentropy',
			// As this is a classification problem you can record accuracy in the logs too!
			metrics: ['accuracy']
		});
	}

	async function handleTrainingFileChange(
		fileList: {
			file: File;
			uuid: string;
		}[]
	) {
		if (!fileList) {
			console.error('No training data selected.');
			return;
		}

		trainingFileList = fileList;
	}

	async function handleCollectionFileChange(
		fileList: {
			file: File;
			uuid: string;
		}[]
	) {
		classifyCollectionImages(fileList);
	}

	async function classifyCollectionImages(
		fileList: {
			file: File;
			uuid: string;
		}[]
	) {
		// Loop through and classify user's images using the pre-trained model
		for (const { file, uuid } of fileList) {
			console.log('Classifying image:', file);
			const reader = new FileReader();
			reader.readAsDataURL(file);
			reader.onloadend = async () => {
				const imageTensor = await preprocessImage(uuid);

				// Use your TensorFlow.js model for classification
				const predictions = model?.predict(imageTensor);

				// Process and display the predictions as needed
				displayPredictions(predictions);
			};
		}
	}

	function preprocessImage(imageData: string): tf.Tensor<tf.Rank> | tf.Tensor<tf.Rank>[] {
		

		if (!mobileNet) {
			console.error('MobileNet model not loaded.');
			return tf.tensor([]); // Return an empty tensor if MobileNet is not loaded
		}

		// Preprocess the image data and convert it to a TensorFlow tensor
		const element = document.getElementById(imageData);
		console.log('Image data:', imageData);
		console.log('Element:', element);

		if (!element) {
			console.error('Image element not found.');
			return tf.tensor([]); // Return an empty tensor if the image element is not found
		}

		const image = tf.browser.fromPixels(element as HTMLImageElement);

		const normalizedImage = tf.cast(image, 'float32').div(tf.scalar(255));
		const batchedImage = normalizedImage.reshape([
			1,
			MOBILE_NET_INPUT_HEIGHT,
			MOBILE_NET_INPUT_WIDTH,
			3
		]);

		// Pass the image through MobileNet to extract features
		const features = mobileNet.predict(batchedImage) as tf.Tensor<tf.Rank> | tf.Tensor<tf.Rank>[];

		return features;
	}

	function displayPredictions(predictions: tf.Tensor | tf.Tensor<tf.Rank>[] | undefined): void {
		// Process and display the predictions as needed
		// You can update the UI to show the predicted classes or confidence scores
		const p = predictions as tf.Tensor<tf.Rank>;
		console.log('Predictions:', p);
		console.log('Predictions shape:', p?.shape);
		console.log('Predictions data:', p?.dataSync());
	}

	loadMobileNetFeatureModel();
	loadCustomModel();
</script>

<svelte:head>
	<title>Capturing Opportunities</title>
</svelte:head>

<div class="index">
	<ImageGrid title="Training Images" handleFileListSubmit={handleTrainingFileChange} />
	<ImageGrid title="Image Collection" handleFileListSubmit={handleCollectionFileChange} />

	<!-- {#if fileList}
		<ImageGrid title="Results" fileListParam={fileList} />
	{/if} -->
</div>

<style>
	.index {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100vh;
	}
</style>
