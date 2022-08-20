import axios from 'axios';
import { AxiosInstance } from 'axios';

export class KioskService {
  protected axiosInstance: AxiosInstance;

  constructor(protected baseURL: string) {
    this.axiosInstance = axios.create({ baseURL });
  }

  async validateIdentityDocument(docFile: File) {
    const formdata = new FormData();
    formdata.append('id_document', docFile);

    const response = await this.axiosInstance.post('/identity-file', formdata, {
      headers: { ContentType: 'multipart/form-data' },
    });

    return response.data;
  }

  async uploadVideo(videoFile: File): Promise<string> {
    const formdata = new FormData();
    formdata.append('video', videoFile);

    const response = await this.axiosInstance.post('/upload-video', formdata, {
      headers: { ContentType: 'multipart/form-data' },
    });

    return response.data.id;
  }

  async checkVideoUploadStatus(videoId: string) {
    const response = await this.axiosInstance.get('/video-indexing-status', {
      params: { video_id: videoId },
    });

    const status = {
      state: response.data.state as string,
      percentage: response.data.videos[0].processingProgress as string,
    };

    return status;
  }

  async validate(
    boardingPassFile: File,
    docFile: File,
    videoFile: File,
    luggageFile: File,
    onVideoStatusUpdate: (response: any) => void,
    onVideoUploadComplete: (response: any) => void,
    pollingTime = 3000
  ) {
    let params = null;

    if (videoFile) {
      const videoId = await this.uploadVideo(videoFile);

      // Check video status
      const videoStatus = await new Promise((resolve, reject) => {
        const timer = setInterval(async () => {
          let status: { state: string; percentage: string };

          try {
            status = await this.checkVideoUploadStatus(videoId);
          } catch (err) {
            reject(err);
          }

          onVideoStatusUpdate(status);

          if (status.state === 'Processed' || status.percentage === '100%') {
            clearInterval(timer);
            resolve(status);
          }
        }, pollingTime);
      });

      onVideoUploadComplete(videoStatus);

      params = {
        video_id: videoId,
      };
    }

    const formData = new FormData();
    if (boardingPassFile) {
      formData.append('boarding_pass', boardingPassFile);
    }
    if (docFile) {
      formData.append('id_document', docFile);
    }
    if (luggageFile) {
      formData.append('luggage', luggageFile);
    }

    const response = await this.axiosInstance.post('/validate', formData, {
      params,
      headers: { ContentType: 'multipart/form-data' },
    });

    return response.data;
  }
}

const kioskService = new KioskService(process.env.VUE_APP_SERVER_HOST);

export default kioskService;
