

export const createSearchArr = (items)=>{
    let searchArr = [];
    items.forEach(element => {
        searchArr.push(element.name)
    });
    return searchArr
}