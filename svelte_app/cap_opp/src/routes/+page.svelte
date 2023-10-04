<script lang="ts">
	import { onMount } from 'svelte';
	import * as tf from '@tensorflow/tfjs';
	// import * as mobilenet from '@tensorflow-models/mobilenet';
	import ImageGrid from './ImageGrid.svelte';
	import type { ImageFile } from '$lib/types';

	const MOBILE_NET_INPUT_WIDTH = 224;
	const MOBILE_NET_INPUT_HEIGHT = 224;

	async function getFeatureExtractor() {
		// const mobilenetModel = await mobilenet.load();
		// const handler = tfn.io.fileSystem(MODEL_URL);
		// const mobilenetModel = await tf.loadGraphModel(handler);

		const URL =
			'https://tfhub.dev/google/tfjs-model/imagenet/mobilenet_v3_small_100_224/feature_vector/5/default/1';
		const mobilenetModel = await tf.loadGraphModel(URL, { fromTFHub: true });
		// Warm up the model by passing zeros through it once.
		tf.tidy(function () {
			let answer = mobilenetModel.predict(
				tf.zeros([1, MOBILE_NET_INPUT_HEIGHT, MOBILE_NET_INPUT_WIDTH, 3])
			) as tf.Tensor;
			console.log(answer.shape);
		});
		// const mobilenetModel = await tf.loadGraphModel(
		// 	'https://tfhub.dev/google/tfjs-model/imagenet/mobilenet_v2_100_224/classification/4/default/1',
		// 	{ fromTFHub: true }
		// );

		const featureExtractor = tf.model({
			inputs: mobilenetModel.inputs,
			outputs: mobilenetModel.layers[87].output // Adjust the layer index as per your needs
		});
		// const featureExtractor = tf.model({
		// 	inputs: mobilenetModel.inputs.map((input) => input as tf.SymbolicTensor),
		// 	outputs: mobilenetModel.outputs as tf.SymbolicTensor[]
		// });

		return featureExtractor;
	}

	function getClassifier() {
		const classifier = tf.sequential();
		classifier.add(tf.layers.flatten({ inputShape: [7, 7, 256] }));
		classifier.add(tf.layers.dense({ units: 1, activation: 'sigmoid' }));

		classifier.compile({
			optimizer: tf.train.adam(),
			loss: 'binaryCrossentropy',
			metrics: ['accuracy']
		});

		return classifier;
	}

	async function trainModel(
		featureExtractor: tf.LayersModel,
		classifier: tf.Sequential,
		trainingImageFiles: ImageFile[]
	) {
		console.log('trainingImageFiles', trainingImageFiles);

		const trainingTensor = tf.stack(
			trainingImageFiles.map(({ file, uuid }) => {
				setTimeout(() => {
					console.log('...waiting');
				}, 5000);

				const element = document.getElementById(uuid);
				console.log('element', element);

				const image = tf.browser.fromPixels(element as HTMLImageElement);
				return tf.image.resizeBilinear(image, [224, 224]).div(255);
			})
		);

		const trainingLabels = tf.ones([trainingImageFiles.length, 1]);

		await classifier.fit(featureExtractor.predict(trainingTensor), trainingLabels, {
			epochs: 10 // Adjust the number of epochs
		});

		return classifier;
	}

	async function classifyCollectionImages(
		featureExtractor: tf.LayersModel,
		classifier: tf.Sequential,
		collectionImageFiles: ImageFile[]
	) {
		const collectionImages = collectionImageFiles.map(({ file, uuid }) => {
			const element = document.getElementById(uuid);

			const image = tf.browser.fromPixels(element as HTMLImageElement);

			return tf.image.resizeBilinear(image, [224, 224]).div(255);
		});

		const predictions = classifier.predict(
			featureExtractor.predict(collectionImages)
		) as tf.Tensor<tf.Rank>;
		const threshold = 0.5;

		const results = predictions.squeeze().arraySync() as number[];

		console.log(
			'Results:',
			results.map((score) => score >= threshold)
		);
	}
	let featureExtractor: tf.LayersModel;
	let classifie: tf.Sequential;

	onMount(async () => {
		featureExtractor = await getFeatureExtractor();
		classifie = getClassifier();
	});

	function handleTrainingFileChange(featureExtractor: tf.LayersModel, classifier: tf.Sequential) {
		return async (fileList: ImageFile[]) =>
			(classifie = await trainModel(featureExtractor, classifier, fileList));
	}

	function handleCollectionFileChange(featureExtractor: tf.LayersModel, classifier: tf.Sequential) {
		return async (fileList: ImageFile[]) => {
			await classifyCollectionImages(featureExtractor, classifier, fileList);
		};
	}
</script>

<svelte:head>
	<title>Capturing Opportunities</title>
</svelte:head>

<div class="index">
	<!-- {#await getFeatureExtractor() then featureExtractor} -->
	{(classifie = getClassifier())}

	<ImageGrid
		title="Training Images"
		handleFileListSubmit={handleTrainingFileChange(featureExtractor, classifie)}
	/>
	<ImageGrid
		title="Image Collection"
		handleFileListSubmit={handleCollectionFileChange(featureExtractor, classifie)}
	/>
	<!-- {/await} -->

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
