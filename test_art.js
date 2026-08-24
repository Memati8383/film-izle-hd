
// Mock DOM
global.window = global;
global.document = {
    createElement: () => ({
        style: {},
        classList: { add: ()=>{}, remove: ()=>{} },
        appendChild: ()=>{},
        addEventListener: ()=>{}
    }),
    querySelector: () => null,
    querySelectorAll: () => []
};
global.navigator = { userAgent: 'node' };
global.HTMLVideoElement = function(){};
global.customElements = { get: ()=>null };

const Artplayer = require('./art.js');
console.log('Artplayer loaded:', typeof Artplayer);
