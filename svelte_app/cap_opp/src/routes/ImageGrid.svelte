<script lang="ts">
	import { v4 as uuidv4 } from 'uuid';
	export let title: string;
	export let fileListParam: FileList | null = null;
	export let handleFileListSubmit: (
		fileList: {
			file: File;
			uuid: string;
		}[]
	) => void;
	let imageGrid: HTMLDivElement;
	let fileList: FileList | null;

	if (fileListParam) {
		populateImageGrid(
			Array.from(fileListParam).map((file) => {
				return { file: file, uuid: uuidv4() };
			})
		);
	} else {
		fileList = null;
	}

	function populateImageGrid(
		fileList: {
			file: File;
			uuid: any;
		}[]
	) {
		const images = fileList.map(({ file, uuid }) => {
			const reader = new FileReader();
			reader.readAsDataURL(file);
			return new Promise<{
				image: string;
				uuid: string;
			}>((resolve) => {
				reader.onloadend = () => {
					resolve({ image: reader.result as string, uuid: uuid });
				};
			});
		});

		Promise.all(images).then((images) => {
			imageGrid.innerHTML = '';
			images.forEach(({ image, uuid }) => {
				const img = document.createElement('img');
				img.src = image as string;
				img.id = uuid;
				img.width = 224;
				img.height = 224;
				imageGrid.appendChild(img);
			});
		});
	}

	function handleFileChange(event: Event) {
		const inputElement = event.target as HTMLInputElement;
		if (inputElement.files) {
			fileList = inputElement.files;

			const testList = Array.from(fileList).map((file) => {
				return { file: file, uuid: uuidv4() };
			});
			populateImageGrid(testList);
			console.log(fileList);
			handleFileListSubmit(testList);
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
