<script lang="ts">
	import ImageGrid from './ImageGrid.svelte';

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

		trainingFileList = fileList;
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

    collectionFileList = fileList;
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
