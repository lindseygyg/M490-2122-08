from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from RunCPR.lib.BallTiltSwitch import BallTiltSwitch
from RunCPR.lib.TouchSwitch import TouchSwitch
from RunCPR.lib.CompressionSystem import CompressionSystem
from RunCPR.lib.MagneticSwitch import MagneticSwitch
from RunCPR.lib.PressureSwitch import PressureSwitch

# Create your views here.
def index(request):
    return render(request, 'Main/index.html')

def aboutTeam(request):
    return render(request, 'Main/aboutTeam.html')

def aboutCPR(request):
    return render(request,'Main/aboutCPR.html')

def start(request):
    return render(request, 'Main/start.html')

def CheckSurroundings(request):
    return render(request, 'Main/CheckSurroundings.html')

def TouchSwitchinstructions(request):
    return render(request, 'Main/TouchSwitchinstructions.html')

def CompressionInstructions(request):
    return render(request, 'Main/CompressionInstructions.html')

def HeadTiltInstructions(request):
    return render(request, 'Main/HeadTiltInstructions.html')

def RescueBreathInstructions(request):
    return render(request, 'Main/RescueBreathInstructions.html')

def AEDinstructions(request):
    return render(request, 'Main/AEDinstructions.html')

def end(request):
    return render(request, 'Main/end.html')

def underConstruction(request):
    return render(request, 'Main/underConstruction.html')


class TouchSwitchView(TemplateView):
    template_name = 'Main/TouchSwitch.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ts = TouchSwitch(pin1=6, pin2=19)
        pulseTime = ts.checkTouch2(t=20)
        pulse_check = False
        if 8 < pulseTime < 12:
            pulse_check = True
            feedback_string = "Good job! Close to 10 seconds is ideal for the pulse check."
        else:
            feedback_string = "Try to feel for the pulse for 10 seconds!"

        context['feedback'] = feedback_string
        context['pulse_time'] = pulseTime
        context['pulse_result'] = pulse_check

        return context

class BallTiltSwitchView(TemplateView):
    template_name = 'Main/balltiltswitch.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bts = BallTiltSwitch(26)
        context['ball_result'] = bts.checkSwitch()

        return context

class PressureSwitchView(TemplateView):
    template_name = 'Main/pressureswitch.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ps = PressureSwitch()
        context['breath_result'] = ps.checkSwitch()

        return context

class MagneticSwitchView(TemplateView):
    template_name = 'Main/magneticswitch.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ms = MagneticSwitch(17,18)
        context['AED_results'] = ms.checkSwitches()

        return context

class CompressionSystemView(TemplateView):
    template_name = 'Main/compressionSystem.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cs = CompressionSystem(24) 
        cycle,freq = cs.checkCompressions()

        if freq > 120:
            feedback_string = "You went a bit too fast! Aim for 100-120 compressions per minute. " \
                              "Sing to the beat of \'Stayin\' Alive\' by the Bee Gees."
        elif freq < 100:
            feedback_string = "Go faster! Sing to the beat of \'Stayin\' Alive\' by the Bee Gees."
        else:
            feedback_string = "Nice frequency!"

        if cycle > 30:
            feedback_string = feedback_string + "\nTry to lower the number of compressions to 30." \
                                                "It helps to count out loud!"
        elif freq < 30:
            feedback_string = feedback_string + "\nTry to do exactly 30 compressions, you did not do enough." \
                                                "It helps to count out loud!"
        else:
            feedback_string = feedback_string + "\nAnd good job with the compressions! 30 is the perfect number."
        
        context['cycle'] = cycle
        context['frequency'] = freq
        context['feedback'] = feedback_string

        return context
