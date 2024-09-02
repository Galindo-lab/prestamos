document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        items: JSON.parse(localStorage.getItem('selectedItems')) || [],

        getItemsLength() {
            return this.items.length;
        },

        addItem(id, name) {
            if (this.items.find(item => item.id === id)) return;

            this.items.push({ id: id, name: name, quantity: 1 });
            localStorage.setItem('selectedItems', JSON.stringify(this.items));
            console.log(this.items);
        },

        removeItem(index) {
            this.items.splice(index, 1);
            localStorage.setItem('selectedItems', JSON.stringify(this.items));
            console.log(this.items);
        },

        updateQuantity(index, quantity) {
            this.items[index].quantity = quantity;
            localStorage.setItem('selectedItems', JSON.stringify(this.items));
        }
    }));
});