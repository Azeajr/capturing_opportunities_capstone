export const useUploadFiles = (url: string, files: FormData,) => {
  return fetch(url, {
    method: "POST",
    body: files,
  })
    .then((res) => res.json()).then((responseData) => {
      console.log('responseData', responseData);
      return responseData;
    })
}