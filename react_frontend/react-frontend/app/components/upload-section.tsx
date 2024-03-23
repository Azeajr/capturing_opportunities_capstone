import React, { useState, useEffect, ChangeEvent } from "react";
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Modal from '@mui/material/Modal';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import LinearProgress from '@mui/material/LinearProgress';
import { useUploadFiles } from "../service/use-upload-files";
import { CollectionData } from '../model/model';

const host = "http://localhost:8000";

const style = {
    position: 'absolute' as 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    border: '2px solid #000',
    boxShadow: 24,
    p: 4,
};

type UploadSectionProps = {
    title: string;
    apiEndpoint: string;
    sendMatchingFiles: (files: File[]) => void;
}

export default function UploadSection(props: UploadSectionProps) {
    const { title, apiEndpoint, sendMatchingFiles } = props;
    const [files, setFiles] = useState<File[]>([]);
    const [scoredFilePaths, setScoredFilePaths] = useState<CollectionData[] | null>(null);
    const [message, setMessage] = useState<string>();
    const [filesMessage, setFilesMessage] = useState<string>();
    const [openModal, setOpenModal] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const buttonSpacing = files.length > 0 ? 'justify-between' : 'gap-10';

    useEffect(() => {
        switch (files.length) {
            case 0:
                setFilesMessage('No files chosen');
                break;
            case 1:
                setFilesMessage(`${files.length} file chosen`);
                break;
            default:
                setFilesMessage(`${files.length} files chosen`);
                break;
        }
    }, [files])

    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        setMessage("");
        const inputFiles = event.target.files;

        if (inputFiles) {
            setFiles([...files, ...Array.from(inputFiles)])
        }
    };

    const removeImage = (fileName: string) => {
        setFiles(files.filter((file) => file.name !== fileName));
    }

    const handleMatchingFiles = (data: CollectionData[]) => {
        // sort the collection response data by score
        const sortedData = data.sort((a, b) => b.attributes.score - a.attributes.score);

        // sort collection files stored in state 
        const sortedFiles: File[] = [];
        sortedData.forEach((d) => {
            files.map((file) => {
                if (d.attributes.imagePath === file.name) {
                    sortedFiles.push(file);
                    // console.log('FILE', file);
                }
            })
        })

        // send sorted files to main page to display matching images
        sendMatchingFiles(sortedFiles);
    }

    // The upload function doesn't directly interact with any DOM events, so it doesn't need a specific event type
    const handleUpload = async () => {
        setMessage("");
        setIsLoading(true);

        if (!files) {
            setMessage("No files selected.");
            setIsLoading(false);
            return;
        }

        const formData = new FormData();

        files.forEach((file) => {
            // formData.append(api_endpoint.split("/").at(-1)!, file);
            formData.append("files", file);
        });

        try {
            const url = `${host}${apiEndpoint}`
            const response = await useUploadFiles(url, formData)
                .then((e) => {
                    console.log("data", e);
                    setMessage(e.meta.message);
                    if (url.includes('collection_images')) {
                        setScoredFilePaths(e.data);
                        handleMatchingFiles(e.data);
                    }
                });

            // if (!response.ok) {
            //     throw new Error(`Error: ${response.statusText}`);
            // }

            // const data = await response.json();
            setIsLoading(false);
        } catch (error) {
            console.error("Upload failed:", error);
            setMessage("Failed to upload files.");
            setIsLoading(false);
        }
    };

    return (
        <div className="p-3 md:w-1/2 w-[360px] bg-white rounded-md">
            <div className="flex flex-row justify-between min-h-10 text-black">
                <h3>{title}</h3>
                {files.length > 0 && message?.length === 0 && !isLoading && (
                    <div>
                        <Button
                            onClick={() => setOpenModal(true)}
                            component="label"
                            variant="outlined"
                            color="error"
                            tabIndex={-1}
                        >
                            Clear Files
                        </Button>
                        <Modal
                            open={openModal}
                            onClose={() => setOpenModal(false)}
                            aria-labelledby="modal-modal-title"
                            aria-describedby="modal-modal-description"
                        >
                            <Box sx={style}>
                                <Typography id="modal-modal-title" variant="h6" component="h2">
                                    Are you sure you want to clear items?
                                </Typography>
                                <Typography id="modal-modal-description" sx={{ mt: 2 }}>
                                    You will have to reupload your items.
                                </Typography>
                                <div className="flex flex-row">
                                    <Button color="error" onClick={() => setOpenModal(false)}>Nevermind</Button>
                                    <Button color="error" onClick={() => { setOpenModal(false); setFiles([]) }}>Clear</Button>
                                </div>

                            </Box>
                        </Modal>
                    </div>
                )}
            </div>
            <div className={`flex flex-row mt-4 ${buttonSpacing}`}>
                <Button
                    component="label"
                    role={undefined}
                    variant="contained"
                    tabIndex={-1}
                >
                    Choose files
                    <input
                        type="file"
                        hidden
                        onChange={handleFileChange}
                        accept="image/*"
                        multiple
                    />
                </Button>
                <span className="align-middle text-black">{filesMessage}</span>
                {files.length > 0 && (
                    <Button
                        onClick={() => { console.log('Submit!', apiEndpoint); handleUpload() }}
                        component="label"
                        variant="contained"
                        color="primary"
                        tabIndex={-1}
                        startIcon={<CloudUploadIcon />}
                        className="align-right"
                    >
                        Upload Files
                    </Button>
                )}
            </div>
            <div className="pt-4 pb-4">
                {isLoading ? (
                    <Box sx={{ width: '100%' }}>
                        <LinearProgress />
                    </Box>
                ) : (
                    <span className="flex justify-center items-center text-[12px] text-red-500">{message}</span>
                )}
            </div>
            <div className="flex flex-wrap gap-2 overflow-scroll h-60">
                {files.map((file, key) => {
                    return (
                        <div key={key} className="overflow-hidden relative">
                            <img onClick={() => { removeImage(file.name); console.log(file.name) }} className="h-20 w-20 rounded-md" src={URL.createObjectURL(file)} />
                        </div>
                    )
                })}
            </div>
        </div>
    );
}
