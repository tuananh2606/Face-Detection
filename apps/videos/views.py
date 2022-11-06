import random
from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from PIL import Image as im
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView, TemplateView
from django.views.generic import View
from django.shortcuts import get_object_or_404, render
import subprocess

import cv2
import numpy as np

from .forms import VideosFileForm
from .models import VideoFile, VideoSet

# Create your views here.
class VideoSetCreateView(CreateView):
    model = VideoSet
    fields = ['name', 'description']

    def form_valid(self, form):
        if not VideoSet.objects.filter(name=form.instance.name).exists():
            return super().form_valid(form)
        else:
            form.add_error(
                'name',
                f"Videoset with name {form.cleaned_data['name']} already exists in dataset. \
                     Add more videos to that imageset, if required."
            )
            return HttpResponseRedirect(reverse('videos:videoset_create_url'))


class VideoSetUpdateView(UpdateView):
    model = VideoSet
    fields = ['name', 'description']

    def form_valid(self, form):
        if not VideoSet.objects.filter(name=form.instance.name).exists():
            return super().form_valid(form)
        else:
            print("entered in else")
            form.add_error(
                'name',
                f"Videoset with name {form.cleaned_data['name']} already exists in dataset. \
                     Add more images to that imageset, if required."
            )
            context = {
                'form': form
            }
            return render(self.request, 'videos/videoset_form.html', context)

    def get_success_url(self):
        return reverse('images:imageset_detail_url', kwargs={'pk': self.object.id})


class VideoSetListView(ListView):
    model = VideoSet
    context_object_name = 'videosets'

    # def get_queryset(self):
    #     return super().get_queryset()

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["user_imagesets"] = ImageSet.objects.all()
    #     print(context)
    #     return context


class VideoSetDetailView(DetailView):
    model = VideoSet
    context_object_name = 'videoset'


class VideosUploadView(View):
    
    # fields = ['name', 'video']

    def get(self, request, *args, **kwargs):
        videoset_id = self.kwargs.get("pk")
        videoset = get_object_or_404(VideoSet, id=videoset_id)
        context = {
            'videoset': videoset,
        }
        return render(request, 'videos/videofile_form.html', context)

    def post(self, request, *args, **kwargs):
        videoset_id = self.kwargs.get("pk")
        videoset = get_object_or_404(VideoSet, id=videoset_id)
        if self.request.method == 'POST':
            videos = self.request.FILES.get("file")
            print(videos.name)
            print(videos.temporary_file_path())

            vid = cv2.VideoCapture(videos.temporary_file_path())
            while(True):
    
                ret, frame = vid.read()

                # Display the resulting frame
                cv2.imshow('frame', frame)
                
                # the 'q' button is set as the
                # quitting button you may use any
                # desired button of your choice
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # After the loop release the cap object
            vid.release()
            # Destroy all the windows
            cv2.destroyAllWindows()

            # for f in request.FILES.getlist('file'):
            #     print(f.name)
            #     video = VideoFile(name=f.name, video=f, video_set=videoset)
            #     video.save()

            # for img in images:
                
            #     if not ImageFile.objects.filter(name=img.name, image_set=imageset).exists():
            #         ImageFile.objects.create(
            #             name=img.name, image=img, image_set=imageset)

            #     else:
            #         print(f"Image {img.name} already exists in the imageset.")

            message = f"Uploading videos to the Imageset: {videoset}. \
                Automatic redirect to the images list after completion."

            redirect_to = reverse_lazy(
                "videos:videos_list_url", args=[videoset_id])
            return JsonResponse({"result": "result",
                                "message": message,
                                 "redirect_to": redirect_to,
                                 "files_length": len(videos),
                                 },
                                status=200,
                                content_type="application/json"
                                )


class VideosListView(ListView):
    model = VideoFile
    context_object_name = 'videos'
    
    def get_queryset(self):
        videoset_id = self.kwargs.get('pk')
        return super().get_queryset().filter(video_set__id=videoset_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        videoset_id = self.kwargs.get('pk')
        videoset = get_object_or_404(VideoSet, id=videoset_id)
        context["videoset"] = videoset
        return context

class VideosDeleteUrl(DeleteView):
    model = VideoFile

    def get_success_url(self):
        qs = self.get_object()
        return qs.get_delete_url()

class VideosetDeleteUrl(DeleteView):
    model = VideoSet

    def get_success_url(self):
        qs = self.get_object()
        return qs.get_delete_url()


# def streamvideo(self):
#     subprocess.run("ls")
#     subprocess.run(['python3', 'detect.py', '--source', os.path.join(uploads_dir, secure_filename(video.filename))])

#     # return os.path.join(uploads_dir, secure_filename(video.filename))
#     obj = secure_filename(video.filename)
#     return obj