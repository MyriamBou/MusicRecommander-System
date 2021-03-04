const example = {
    name: 'example',
    template: '#example',
    components: {
      VueGridMultiselect },
  
    data() {
      return {
        selectedItems: null,
        items: [
        { id: 1, name: "San Francisco", state: "USA", info: "San Francisco information" },
        { id: 2, name: "Las Vegas", state: "USA", info: "Las Vegas information" },
        { id: 3, name: "Washington", state: "USA", info: "Washington information" },
        { id: 4, name: "Munich", state: "Germany", info: "Munich information" }] };
  
  
    },
    methods: {
      save() {
        alert('Save');
      },
      cancel() {
        alert('Cancel');
      } } };
  
  
  
  new Vue({
    el: '.vue-app',
    components: {
      example } });