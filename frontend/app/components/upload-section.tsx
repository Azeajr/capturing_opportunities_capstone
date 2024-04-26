import React, { useState, useEffect, ChangeEvent } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Modal from "@mui/material/Modal";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import LinearProgress from "@mui/material/LinearProgress";
import InfoIcon from "@mui/icons-material/Info";
import Tooltip from "@mui/material/Tooltip";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import { CollectionData } from "../model/model";

// const host = "http://localhost:8000";

const style = {
  position: "absolute" as "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: 400,
  bgcolor: "background.paper",
  border: "2px solid #000",
  boxShadow: 24,
  p: 4,
};

type UploadSectionProps = {
  title: string;
  apiEndpoint: string;
  model?: string;
  sendMatchingFiles: (files: File[]) => void;
  setCollectionEndpoint: (endpoint: string) => void;
  setSesstionId?: (sessionId: string) => void;
};

export default function UploadSection(props: UploadSectionProps) {
  const {
    title,
    apiEndpoint,
    model,
    sendMatchingFiles,
    setCollectionEndpoint,
    setSesstionId,
  } = props;
  const [files, setFiles] = useState<File[]>([]);
  const [scoredFilePaths, setScoredFilePaths] = useState<
    CollectionData[] | null
  >(null);
  const [message, setMessage] = useState<string>();
  const [filesMessage, setFilesMessage] = useState<string>();
  const [openModal, setOpenModal] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [selectedModel, setModel] = useState<string>(model ? model : "svm");
  const isTraining = apiEndpoint.includes("training_images");
  const isCollection = apiEndpoint.includes("collection_images");
  const buttonSpacing = files.length > 0 ? "justify-between" : "gap-10";
  const isABTestingEnabled =
    process.env.NEXT_PUBLIC_AB_TESTING_ENABLED === "true";

  const handleModelChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setModel((event.target as HTMLInputElement).value);
  };

  const handleToggleChange = (
    event: React.MouseEvent<HTMLElement>,
    newAlignment: string
  ) => {
    if (newAlignment !== null) setModel(newAlignment);
  };

  useEffect(() => {
    switch (files.length) {
      case 0:
        setFilesMessage("No files chosen");
        break;
      case 1:
        setFilesMessage(`${files.length} file chosen`);
        break;
      default:
        setFilesMessage(`${files.length} files chosen`);
        break;
    }
  }, [files]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setMessage("");
    const inputFiles = event.target.files;

    if (inputFiles) {
      setFiles([...files, ...Array.from(inputFiles)]);
    }
  };

  const removeImage = (fileName: string) => {
    setFiles(files.filter((file) => file.name !== fileName));
  };

  const handleMatchingFiles = (data: CollectionData[]) => {
    // sort the collection response data by score
    const sortedData = data.sort(
      (a, b) => a.attributes.score - b.attributes.score
    );
    console.log(sortedData);

    // sort collection files stored in state
    const sortedFiles: File[] = [];
    sortedData.forEach((d) => {
      files.map((file) => {
        if (d.attributes.imagePath === file.name) {
          sortedFiles.push(file);
          // console.log('FILE', file);
        }
      });
    });
    console.log(sortedFiles);
    // send sorted files to main page to display matching images
    sendMatchingFiles(sortedFiles);
  };

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
      // const url = isTraining ? `${host}${apiEndpoint}/${selectedModel}` : `${host}${apiEndpoint}`
      const url = isTraining
        ? `/api${apiEndpoint}/${selectedModel}`
        : `/api${apiEndpoint}`;
      const response = await fetch(url, {
        method: "POST",
        body: formData,
      });

      const responseJson = await response.json();

      console.log("data", responseJson);
      setMessage(responseJson.meta.message);
      if (isTraining && responseJson.data.attributes.collectionApiEndpoint) {
        setCollectionEndpoint(
          responseJson.data.attributes.collectionApiEndpoint
        );
      }
      if (isCollection) {
        setScoredFilePaths(responseJson.data);
        handleMatchingFiles(responseJson.data);
        setSesstionId ? setSesstionId(responseJson.meta.sessionId) : null;
      }

      //   const response = await fetch(url, {
      //     method: "POST",
      //     body: formData,
      //   });
      //   const responseJson = await response.json();

      //   console.log("data", responseJson);
      //   setMessage(responseJson.meta.message);
      //   if (isTraining && responseJson.data.attributes.collectionApiEndpoint) {
      //     setCollectionEndpoint(
      //       responseJson.data.attributes.collectionApiEndpoint
      //     );
      //   }
      //   if (isCollection) {
      //     setScoredFilePaths(responseJson.data);
      //     handleMatchingFiles(responseJson.data);
      //   }

      //   if (!response.ok) {
      //     throw new Error(`Error: ${response.statusText}`);
      //   }

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
                  <Button color="error" onClick={() => setOpenModal(false)}>
                    Nevermind
                  </Button>
                  <Button
                    color="error"
                    onClick={() => {
                      setOpenModal(false);
                      setFiles([]);
                    }}
                  >
                    Clear
                  </Button>
                </div>
              </Box>
            </Modal>
          </div>
        )}
      </div>
      {isTraining && !isABTestingEnabled ? (
        <div>
          <FormControl>
            <FormLabel id="demo-controlled-radio-buttons-group">
              Choose a model to train
            </FormLabel>
            <div className="flex flex-row">
              <ToggleButtonGroup
                color="primary"
                value={selectedModel}
                exclusive
                onChange={handleToggleChange}
                aria-label="Model"
              >
                <ToggleButton value="svm">
                  <span className="pr-2">SVM</span>
                  <Tooltip title="A support vector machine (SVM) is a supervised machine learning algorithm that classifies data by finding an optimal line or hyperplane that maximizes the distance between each class in an N-dimensional space">
                    <InfoIcon />
                  </Tooltip>
                </ToggleButton>
                <ToggleButton value="auto_encoder">
                  <span className="pr-2">Auto encoder</span>
                  <Tooltip title="An autoencoder is a type of artificial neural network used to learn efficient codings of unlabeled data.">
                    <InfoIcon />
                  </Tooltip>
                </ToggleButton>
              </ToggleButtonGroup>
            </div>
          </FormControl>
        </div>
      ) : (
        <div className="h-16"></div>
      )}

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
            onClick={() => {
              console.log("Submit!", apiEndpoint);
              handleUpload();
            }}
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
          <Box sx={{ width: "100%" }}>
            <LinearProgress />
          </Box>
        ) : (
          <span className="flex justify-center items-center text-[12px] text-red-500">
            {message}
          </span>
        )}
      </div>
      <div className="flex flex-wrap gap-2 overflow-scroll h-60">
        {files.map((file, key) => {
          return (
            <div key={key} className="overflow-hidden relative">
              <img
                onClick={() => {
                  removeImage(file.name);
                  console.log(file.name);
                }}
                className="h-20 w-20 rounded-md"
                src={URL.createObjectURL(file)}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
