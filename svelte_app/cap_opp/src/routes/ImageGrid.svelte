<script lang="ts">
	export let title: string;
	export let fileListParam: FileList | null = null;
	let imageGrid: HTMLDivElement;
	let fileList: FileList | null;

	if (fileListParam) {
		populateImageGrid(fileListParam);
	} else {
		fileList = null;
	}

	function populateImageGrid(fileList: FileList) {
		const images = Array.from(fileList).map((file) => {
			const reader = new FileReader();
			reader.readAsDataURL(file);
			return new Promise((resolve) => {
				reader.onloadend = () => {
					resolve(reader.result);
				};
			});
		});

		Promise.all(images).then((images) => {
			imageGrid.innerHTML = '';
			images.forEach((image) => {
				const img = document.createElement('img');
				img.src = image as string;
				imageGrid.appendChild(img);
			});
		});
	}

	function handleFileChange(event: Event) {
		const inputElement = event.target as HTMLInputElement;
		if (inputElement.files) {
			fileList = inputElement.files;
			populateImageGrid(fileList);
			console.log(fileList);
		}
	}
</script>

<h1>{title}</h1>
{#if !fileListParam}
	<input on:change={handleFileChange} type="file" id="many" multiple />
{/if}

<div class="image-grid" bind:this={imageGrid} />

<style>
	.image-grid {
		width: 300px;
		min-height: 100px;
		border: 2px solid #ddd;
		margin-top: 15px;
		display: flex;
		align-items: center;
		justify-content: center;
	}
</style>
