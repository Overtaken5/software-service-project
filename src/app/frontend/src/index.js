import './styles/style.scss';
import {searchHelper,debounce} from './assets/search';
import {getAllProducts,getProductDetails,fetchProductForecast,fetchForecastGraph} from './api/api_request';
import {createSearchArr} from './assets/chenge_data';
import {productItem} from './Products'

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('searchInput');
  const searchButton = document.getElementById('searchButton');
  const faqItemsContainer = document.getElementById('faqItemsContainer');
  const faqItemTemplate = document.getElementById('faqItemTemplate');
  const suggestionsList = document.getElementById('suggestions');
  const monthSelector = document.getElementById('monthSelector')
  let Product = []; 

  const fetchItems = async (query, months_ahead) => {
    try {
      const data = await fetchProductForecast(query, months_ahead);
      if (data) {
        console.log(data.forecast);
        const productItem_ = new productItem(
          data.product_name,
          data.product_price,
          data.forecast[0].date,
          data.forecast[0].quantity,
          data.product_id
        );
        console.log(productItem_);
        return productItem_; 
      }
    } catch (error) {
      console.log(error);
      return null; 
    }
  };

  getAllProducts()
    .then((data) => {
      console.log(data);
      const namedProduct = createSearchArr(data);
      console.log(namedProduct);
      Product = [...Product, ...namedProduct];
      console.log('Updated Product array:', Product);
      searchHelper(Product,suggestionsList)
    })
    .catch((error) => {
      console.error('Нет соединения с сервером');
    })
    .finally(() => {
      console.log('...');
    });


   
    const createFaqItem = (item) => {
      const faqItem = faqItemTemplate.content.cloneNode(true);
      faqItem.querySelector('.item-name').textContent = item.name;
      faqItem.querySelector('.item-date').textContent = item.date;
      faqItem.querySelector('.item-quantity').textContent = item.quantity;
      faqItem.querySelector('.item-price').textContent = `$${item.price}`;
      const graphImage = faqItem.querySelector('.graph_image');
      const expandBtn = faqItem.querySelector('.expand-btn');
      const answer = faqItem.querySelector('.answer');
  
      expandBtn.addEventListener('click', async () => {
        try {
          
          const imageUrl = await fetchForecastGraph(item.name, monthSelector.value);
          if (imageUrl) {
            console.log(imageUrl)
            graphImage.src = imageUrl;
            graphImage.alt = "График прогноза";
          } else {
            console.error("Ошибка загрузки графика");
          }
          answer.classList.toggle('visible');
          if(expandBtn.textContent =="+"){
            expandBtn.textContent = "-";
          }else{
            expandBtn.textContent = "+";
          }
        } catch (error) {
          console.error("Ошибка при обработке графика:", error);
        }
      });
  
      return faqItem;
    };


    searchButton.addEventListener('click', async () => {
      const query = searchInput.value.trim();
      if (!query) {
        alert('Введите текст для поиска!');
        return;
      }
    
      const notFoundMessage = faqItemsContainer.querySelector('.not-found-message');
      if (notFoundMessage) {
        notFoundMessage.remove();
      }
    
      faqItemsContainer.insertAdjacentHTML('beforeend', '<p class="loading">Загрузка...</p>');
    
      const item = await fetchItems(query, monthSelector.value);
    
      const loadingIndicator = faqItemsContainer.querySelector('.loading');
      if (loadingIndicator) {
        loadingIndicator.remove();
      }
    
      if (item) {

        const isDuplicate = Array.from(faqItemsContainer.children).some((child) => {
          return child.querySelector('.item-name')?.textContent === item.name;
        });
    
        if (isDuplicate) {
          alert('Товар с таким названием уже добавлен!');
          return;
        }
    
        const faqItem = createFaqItem(item);
        faqItemsContainer.appendChild(faqItem);
      } else {
        const message = document.createElement('p');
        message.className = 'not-found-message';
        message.textContent = 'Товары не найдены.';
        faqItemsContainer.appendChild(message);
      }
    });

});
