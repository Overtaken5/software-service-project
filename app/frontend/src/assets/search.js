export const products = [
    'Телевизор Samsung',
    'Мобильный телефон iPhone',
    'Наушники Sony',
    'Планшет Huawei',
    'Ноутбук Dell',
    'Умные часы Apple Watch',
    'Кофеварка Bosch',
    'Стиральная машина LG',
    'Микроволновая печь Panasonic',
    'Холодильник Samsung',
  ];

  export function debounce(func, delay) {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), delay);
    };
  }