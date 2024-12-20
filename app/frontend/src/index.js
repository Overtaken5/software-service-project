import './styles/style.scss';
 import {searchHelper,debounce} from './assets/search';
import {getAllProducts,getProductDetails} from './api/api_request';
import {createSearchArr} from './assets/chenge_data';

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('searchInput');
  const searchButton = document.getElementById('searchButton');
  const faqItemsContainer = document.getElementById('faqItemsContainer');
  const faqItemTemplate = document.getElementById('faqItemTemplate');
  const suggestionsList = document.getElementById('suggestions');
  let Product = []; 

  const fetchItems = async (query) => {

    getProductDetails('Product 1')
      .then((data) =>{ 
        console.log('POST Response:', data)
      })
      .catch((error) => console.error('Error:', error));

    const mockData = [
      { name: 'Product A', date: '2024-12-19', quantity: 10, price: 25 },
      { name: 'Product B', date: '2024-11-15', quantity: 5, price: 15 },
      { name: 'Product C', date: '2024-10-10', quantity: 20, price: 50 },
    ];

    await new Promise((resolve) => setTimeout(resolve, 500));
    return mockData.filter((item) => item.name.toLowerCase().includes(query.toLowerCase()));

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

  // getProductDetails('Product 1')
  // .then((data) => console.log('POST Response:', data))
  // .catch((error) => console.error('Error:', error));


  const createFaqItem = (item) => {

    const faqItem = faqItemTemplate.content.cloneNode(true);
    faqItem.querySelector('.item-name').textContent = item.name;
    faqItem.querySelector('.item-date').textContent = item.date;
    faqItem.querySelector('.item-quantity').textContent = item.quantity;
    faqItem.querySelector('.item-price').textContent = `$${item.price}`;

    const expandBtn = faqItem.querySelector('.expand-btn');
    const answer = faqItem.querySelector('.answer');
    expandBtn.addEventListener('click', () => {
      answer.classList.toggle('visible');
    });

    return faqItem;
  };


  searchButton.addEventListener('click', async () => {
    const query = searchInput.value.trim();
    if (!query) {
      alert('Введите текст для поиска!');
      return;
    }

    if(faqItemsContainer.querySelector('.not-found-message')){
      faqItemsContainer.querySelector('.not-found-message').remove()
    }

    faqItemsContainer.insertAdjacentHTML('beforeend', '<p class="loading">Загрузка...</p>');
    const items = await fetchItems(query);

    const loadingIndicator = faqItemsContainer.querySelector('.loading');
    if (loadingIndicator) {
      loadingIndicator.remove();
    }

    if (items.length > 0) {
      items.forEach((item) => {
        const faqItem = createFaqItem(item);
        faqItemsContainer.appendChild(faqItem);
      });
    } else {
      const message = document.createElement('p');
      message.className = 'not-found-message';
      message.textContent = 'Товары не найдены.';
      faqItemsContainer.appendChild(message);
    }
  });



  // searchInput.addEventListener('input', (e) => {
  //   const query = e.target.value.toLowerCase().trim();
  //   suggestionsList.innerHTML = ''; 
  
  //   if (query) {
  //     const filteredProducts = products.filter((product) =>
  //       product.toLowerCase().startsWith(query)
  //     );
  
  //     filteredProducts.forEach((product) => {
  //       const li = document.createElement('li');
  
  //       const matchedText = product.slice(0, query.length);
  //       const unmatchedText = product.slice(query.length);
  
  //       li.innerHTML = `
  //         <span class="matched">${matchedText}</span>
  //         <span class="unmatched">${unmatchedText}</span>
  //       `;
  
  //       li.addEventListener('click', () => {
  //         searchInput.value = product;  
  //         suggestionsList.innerHTML = ''; 
  //       });
  
  //       suggestionsList.appendChild(li);
  //     });
  //   }
  // });
});
