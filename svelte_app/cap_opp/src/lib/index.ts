// import * as tf from '@tensorflow/tfjs';

// // tf.ke

// // export function ml_lib() {

// // }

// const tf = require('@tensorflow/tfjs-node');
// const fs = require('fs');
// const path = require('path');
// const { promisify } = require('util');
// const readdir = promisify(fs.readdir);
// const sharp = require('sharp');

// const imageDir = 'dataset/train'; // Adjust the directory paths
// const validationDir = 'dataset/validate';

// // Data preprocessing
// const preprocessImage = async (filePath:any, targetSize:any) => {
// 	const imageBuffer = await sharp(filePath).resize(targetSize[0], targetSize[1]).toBuffer();
// 	return tf.node.decodeImage(imageBuffer, 3);
// };

// const readImagesFromDirectory = async (directoryPath, targetSize) => {
// 	const imagePaths = await readdir(directoryPath);
// 	const images = [];

// 	for (const imagePath of imagePaths) {
// 		const fullPath = path.join(directoryPath, imagePath);
// 		const image = await preprocessImage(fullPath, targetSize);
// 		images.push(image);
// 	}

// 	return tf.stack(images);
// };

// (async () => {
// 	const targetSize = [224, 224];

// 	const trainImages = await readImagesFromDirectory(imageDir, targetSize);
// 	const validationImages = await readImagesFromDirectory(validationDir, targetSize);

// 	const trainLabels = tf.tensor([...Array(trainImages.shape[0]).keys()]); // Modify for your binary labels
// 	const validationLabels = tf.tensor([...Array(validationImages.shape[0]).keys()]); // Modify for your binary labels

// 	// Model creation
// 	const baseModel = await tf.loadLayersModel(
// 		'https://tfhub.dev/tensorflow/resnet_50/classification/1'
// 	);
// 	const x = baseModel.predict(trainImages);
// 	const output = tf.layers.dense({ units: 1, activation: 'sigmoid' }).apply(x);
// 	const model = tf.model({ inputs: baseModel.input, outputs: output });

// 	// Model compilation
// 	model.compile({ optimizer: 'adam', loss: 'binaryCrossentropy', metrics: ['accuracy'] });

// 	// Model training
// 	await model.fit(trainImages, trainLabels, {
// 		epochs: 10,
// 		validationData: [validationImages, validationLabels]
// 	});

// 	const timestamp = new Date().toISOString().replace(/:/g, '-');
// 	await model.save(`file://${path.join(__dirname, `models/model-${timestamp}`)}`);

// 	// Predict new images
// 	const newImage = await preprocessImage('00_001.png', targetSize);
// 	const newImages = tf.stack([newImage]);
// 	const prediction = await model.predict(newImages).data();

// 	if (prediction[0] >= 0.5) {
// 		console.log('Image belongs to the group.');
// 	} else {
// 		console.log('Image does not belong to the group.');
// 	}
// })();
