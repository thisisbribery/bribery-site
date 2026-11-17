# Screenshot the Bribeluge Companion at 1280x800 with a plausible demo state fed in,
# so the tablet screen in the render shows a live-looking app rather than "Not connected".
from playwright.sync_api import sync_playwright
import sys
INJECT = r"""
() => {
  try { setDetected('bribes'); } catch (e) {}
  setStatus('Connected · Deluge', 'ok');
  state = {kind:'state', seq:1, version:1, outType:0, synthMode:0, osc0:5, engine:16, engineSub:0, track:2, row:127,
           name:'BRIB PAD 3', rowName:''};
  stateCount = 412;
  render();
  showTransport({playing:true, recording:false, arrangement:false, metronome:false, bpm:12400, view:4});
  var K = [], x = 0;
  function k(g, name, pos, bip, val) { K.push({x:x%16, y:Math.floor(x/16), group:g, bipolar:!!bip, open:false, cant:false, wide:false,
      pos:pos, value:val===undefined?Math.round(pos/127*50):val, name:name, text:'', isSwitch:false}); x++; }
  function sw(g, name, text) { K.push({x:x%16, y:Math.floor(x/16), group:g, bipolar:false, open:false, cant:false, wide:false,
      pos:0, value:0, name:name, text:text, isSwitch:true}); x++; }
  k(7,'CUTOFF',92); k(7,'RESO',58); k(7,'ENV AMT',74); k(7,'DRIFT',30); k(7,'PWM',66); k(7,'DETUNE',40,1,6);
  sw(8,'VOICES','POLY'); sw(8,'UNISON','OFF');
  k(0,'OSC1 VOL',110); k(0,'OSC2 VOL',80); k(0,'OSC2 PITCH',64,1,7); k(0,'NOISE',12);
  k(1,'LPF FREQ',88); k(1,'LPF RES',44); k(1,'HPF FREQ',14);
  k(2,'ATTACK',36); k(2,'DECAY',70); k(2,'SUSTAIN',96); k(2,'RELEASE',82);
  k(5,'REVERB',72); k(5,'DELAY',48); k(5,'SATURATE',22);
  K[0].open = true;
  showParams({kind:'params', open:true, knobs:K});
  var G = [], gn = ['VOLUME','PAN','CUTOFF','RESO','ATTACK','RELEASE','AMOUNT','RATE','REVERB','DELAY','MOD RATE','MOD DEPTH','STUTTER','SIDECHAIN','PITCH','LFO'];
  for (var i = 0; i < 16; i++) G.push({bipolar: i===1||i===14, none:false, pos:[100,64,92,58,30,80,64,40,72,48,60,36,0,20,64,50][i], value:[38,0,36,23,12,31,25,16,28,19,24,14,0,8,0,20][i], name:gn[i]});
  showGold({kind:'gold', open:true, mode:1, knobs:G});
  // 7-seg: "124." style digits as segment masks (bit 6=A .. 0=G, 7=dp)
  showDigits([0x00, 0x30, 0x6D, 0x33]);
  showText({main:'CUTOFF', mainEnglish:'Cutoff  92', popup:false, popupText:'', popupEnglish:'', menu:'BROPHET'});
  updateStage();
}
"""
out = sys.argv[1] if len(sys.argv) > 1 else 'companion_screen.png'
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width':1280,'height':800}, device_scale_factor=1)
    pg.goto('http://127.0.0.1:8796/index.html')
    pg.wait_for_timeout(1200)
    pg.evaluate(INJECT)
    pg.wait_for_timeout(600)
    pg.screenshot(path=out)
    b.close()
