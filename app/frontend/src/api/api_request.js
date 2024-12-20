
const getResponseData = (response) => {
    if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
};
// http://127.0.0.1:8227/all_products
const config = {
    baseUrl: 'http://127.0.0.1:8227',
    headers: {
        'Content-Type': 'application/json',
      },
};

export const getAllProducts = () => {
    return fetch(`${config.baseUrl}/all_products`,{
        method: 'GET',
        headers: config.headers,
    }).then(response =>{
        if (!response.ok){
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json()
    });
};