<script lang="ts">
	import ImageGrid from './ImageGrid.svelte';

	let fileList: FileList | null = null;

	function handleFileChange(event: Event) {
		const inputElement = event.target as HTMLInputElement;
		if (inputElement.files) {
			fileList = inputElement.files;
		}
	}
</script>

<div class="index">
	<h1>Capturing Opportunities</h1>
	<ImageGrid title="Training Images" />
	<ImageGrid title="Testing Images" />
	<h3>Fake Input</h3>
	<p>This is meant to emulate how a library will eventually return a filelist of results</p>
	<input type="file" id="many" multiple on:change={handleFileChange} />
	{#if fileList}
		<ImageGrid title="Results" fileListParam={fileList} />
	{/if}
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
