
const getResponseData = (response) => {
    if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
};

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

export const getProductDetails = (productName) => {
    return fetch(`${config.baseUrl}/one_product_amount`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            product_name: productName,
        }),
    }).then((response) => {
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }
        return response.json();
    });
};

export const fetchProductForecast = async (productName, monthsAhead) => {
    const url = "http://127.0.0.1:8227/product_forecast"; 
  
    const formData = new URLSearchParams();
    formData.append("product_name", productName);
    formData.append("months_ahead", monthsAhead);
  
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка при запросе");
      }
  
      const data = await response.json();
      console.log("Результат прогноза:", data);
      return data;

    } catch (error) {
      console.error("Ошибка:", error.message);
    }
  };

  export const fetchForecastGraph = async (productName, monthsAhead) => {
    const url = "http://127.0.0.1:8227/product_forecast_graph";
  
    const formData = new URLSearchParams();
    formData.append("product_name", productName);
    formData.append("months_ahead", monthsAhead);
  
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Ошибка при запросе графика прогноза");
      }
  
      const blob = await response.blob();
      const imageUrl = URL.createObjectURL(blob);
      return imageUrl; 
    } catch (error) {
      console.error("Ошибка:", error.message);

      return null;
    }
  };