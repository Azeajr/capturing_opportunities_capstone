<script lang="ts">
	import ImageGrid from './ImageGrid.svelte';

	const host = 'http://localhost:8000';

	const training_endpoint = '/uploads/training_images';
	const collection_endpoint = '/uploads/collection_images';

	let trainingFileList: { file: File; uuid: string }[] = [];
	let collectionFileList: { file: File; uuid: string }[] = [];

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

		// trainingFileList = fileList;
		const formData = new FormData();
		fileList.forEach((file) => {
			formData.append('files', file.file);
		});

		const response = await fetch(`${host}${training_endpoint}`, {
			method: 'POST',
			body: formData
		});

		const data = await response.json();

		console.log(data);
	}

	async function handleCollectionFileChange(
		fileList: {
			file: File;
			uuid: string;
		}[]
	) {
		if (!fileList) {
			console.error('No collection data selected.');
			return;
		}

		// collectionFileList = fileList;

		const formData = new FormData();
		fileList.forEach((file) => {
			formData.append('files', file.file);
		});

		const response = await fetch(`${host}${collection_endpoint}`, {
			method: 'POST',
			body: formData
		});

		const data = await response.json();

		console.log(data);
	}
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
