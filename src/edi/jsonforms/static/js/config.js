require.config({
    baseUrl: '++resource++edi.jsonforms/js',
    paths: {
        'vue-json-form': 'vue-json-form.umd'
    }
});

require(['vue-json-form'], function(Vue) {
    console.log('Vue loaded:', Vue);
});
