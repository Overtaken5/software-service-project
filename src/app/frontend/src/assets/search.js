

  export function debounce(func, delay) {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), delay);
    };
  }

  export function searchHelper(products,suggestionsList){
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      suggestionsList.innerHTML = ''; 
    
      if (query) {
        const filteredProducts = products.filter((product) =>
          product.toLowerCase().startsWith(query)
        );
    
        filteredProducts.forEach((product) => {
          const li = document.createElement('li');
    
          const matchedText = product.slice(0, query.length);
          const unmatchedText = product.slice(query.length);
    
          li.innerHTML = `
            <span class="matched">${matchedText}</span>
            <span class="unmatched">${unmatchedText}</span>
          `;
    
          li.addEventListener('click', () => {
            searchInput.value = product;  
            suggestionsList.innerHTML = ''; 
          });
    
          suggestionsList.appendChild(li);
        });
      }
    });
  }