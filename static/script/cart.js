document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({
        items: JSON.parse(localStorage.getItem('selectedItems')) || [],

        init() {
            // Actualiza el valor de id_form-TOTAL_FORMS al cargar la página
            this.updateTotalForms();
        },

        getItemsLength() {
            return this.items.length;
        },

        addItem(id, name, imageUrl) {
            if (this.items.find(item => item.id === id)) return;

            this.items.push({id: id, name: name, quantity: 1, imageUrl: imageUrl});
            localStorage.setItem('selectedItems', JSON.stringify(this.items));
            this.updateTotalForms(); // Actualiza el valor de TOTAL_FORMS
            console.log(this.items);
        },

        removeItem(index) {
            this.items.splice(index, 1);
            localStorage.setItem('selectedItems', JSON.stringify(this.items));
            this.updateTotalForms(); // Actualiza el valor de TOTAL_FORMS
            console.log(this.items);
        },

        updateQuantity(index, quantity) {
            this.items[index].quantity = quantity;
            localStorage.setItem('selectedItems', JSON.stringify(this.items));
        },

        increaseQuantity(index) {
            this.items[index].quantity += 1;
            localStorage.setItem('selectedItems', JSON.stringify(this.items));
        },

        decreaseQuantity(index) {
            if (this.items[index].quantity > 1) {
                this.items[index].quantity -= 1;
                localStorage.setItem('selectedItems', JSON.stringify(this.items));
            }
        },

        // Nueva función para comprobar si el artículo ya está agregado
        isItemAdded(id) {
            return this.items.some(item => item.id === id);
        },


        updateTotalForms() {
            const totalForms = document.getElementById('id_form-TOTAL_FORMS');
            if (totalForms) {
                totalForms.value = this.items.length;
            }
        }
    }));

    // Escuchar evento antes de abandonar la página para asegurar sincronización
    window.addEventListener('beforeunload', () => {
        localStorage.setItem('selectedItems', JSON.stringify(Alpine.store('app').items));
    });
});
