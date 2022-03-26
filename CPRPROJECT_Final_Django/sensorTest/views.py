from django.shortcuts import render
from django.views.generic import TemplateView
from sensorTest.lib.BallTiltSwitch import BallTiltSwitch
from sensorTest.lib.TouchSwitch import TouchSwitch
from sensorTest.lib.CompressionSystem import CompressionSystem
from sensorTest.lib.MagneticSwitch import MagneticSwitch
from sensorTest.lib.PressureSwitch import PressureSwitch

def TestSensor(request):
    return render(request, 'Main/testsensor.html')

def TestTouchSwitch(request):
    return render(request, 'Main/TouchSwitchTest.html')

class TouchSwitchResults(TemplateView):
    template_name = 'Main/TouchSwitchResults.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ts = TouchSwitch(pin1=6, pin2=19)
        
        touch_result = ts.testSwitch()
        context['touch_result'] = touch_result

        return context
    

def TestBallTiltSwitch(request):
    return render(request, 'Main/BallTiltSwitchTest.html')

class BallTiltResults(TemplateView):
    template_name = 'Main/BallTiltSwitchResults.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bts = BallTiltSwitch(26)
        check_value = False
        tilt_result = bts.checkSwitch()
      
        context['tilt_result'] = tilt_result

        return context
    
    
def TestPressureSwitch(request):
    return render(request, 'Main/PressureSwitchTest.html')

class PressureSwitchResults(TemplateView):
    template_name = 'Main/PressureSwitchResults.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ps = PressureSwitch()
        
        ps_result = ps.pressure_check(10)
        context['ps_result'] = ps_result

        return context
    
def TestMagneticSwitch(request):
    return render(request, 'Main/MagneticSwitchTest.html')

class MagneticSwitchResults(TemplateView):
    template_name = 'Main/MagneticSwitchResults.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ms = MagneticSwitch(17, 18)
        
        ms_result = ms.checkSwitches()
        context['ms_result'] = ms_result

        return context
    

def CompressionTest(request):
    return render (request, 'Main/CompressionTest.html')

class CompressionSystemResults(TemplateView):
    template_name = 'Main/CompressionResults.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cs = CompressionSystem(24)
        cycle = cs.checkCompressions()
        
        context['cycle'] = cycle

        return context
