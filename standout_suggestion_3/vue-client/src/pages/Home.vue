<template>
  <v-container fluid fill-height>
    <v-layout row justify-space-around align-center justify-center>
      <v-flex xs6>
        <v-card>
          <v-card-title> Please validate your boarding </v-card-title>
          <v-card-text>
            Select your documents to validate with your flight manifest information
            <!-- </v-card-text> -->
            <!-- <v-card-actions> -->
            <br />
            <br />
            <v-row align="center" justify="space-around">
              <v-btn color="deep-orange" @click="openModal(data.boardingPass)"
                >Select boarding pass
              </v-btn>
              <v-btn color="purple" @click="openModal(data.identityDoc)"
                >Select identity document
              </v-btn>
              <v-btn color="pink" @click="openModal(data.video)"
                >Select your verification video
              </v-btn>
            </v-row>
            <br />
            <br />
            <v-row align="center" justify="space-around">
              <v-btn color="cyan" @click="openModal(data.luggage)">Select your luggage </v-btn>
              <!-- <v-btn color="grey" @click="openModal(data.businessCard)"
                >(Optional) Select your business card
              </v-btn> -->
            </v-row>
            <br />
            <br />
            <v-row align="center" justify="space-around">
              <v-btn block x-large color="success" @click="validate">Validate Boarding </v-btn>
              <!-- <v-btn block x-large color="success" @click="openValidationDialog"
                >Validation Result
              </v-btn> -->
            </v-row>
          </v-card-text>
        </v-card>
      </v-flex>
      <file-dialog
        :title="currentDataItem.title"
        :show-dialog="showModal"
        :is-image="currentDataItem.isImage"
        :is-video="currentDataItem.isVideo"
        :accept="currentDataItem.accept"
        :selected-file="currentDataItem.fileResult"
        @close="onModalClosed"
        @selected="onModalResult"
      ></file-dialog>
      <status-dialog
        ref="validationDialog"
        :show-dialog="showValidationDialog"
        :validation-ready="validationReady"
        @close="onValidationModalClosed"
      >
      </status-dialog>
    </v-layout>
  </v-container>
</template>

<script lang="ts">
import { Component, Ref, Vue } from 'vue-property-decorator';
import FileDialog from '@/components/file-dialog.vue';
import StatusDialog from '@/components/status-dialog.vue';
import kioskService, { KioskService } from '@/services/kiosk.service';
import { FileResult } from '@/utils/file.util';
import { namespace } from 'vuex-class';

const data = {
  boardingPass: {
    title: 'Select your boarding pass document',
    isImage: true,
    isVideo: false,
    accept: 'image/*,.pdf',
    fileResult: {
      file: null,
      dataURL: '',
    } as FileResult,
  },
  identityDoc: {
    title: 'Select your identity document',
    isImage: true,
    isVideo: false,
    accept: 'image/*,.pdf',
    fileResult: {
      file: null,
      dataURL: '',
    } as FileResult,
  },
  video: {
    title: 'Select your verification video file',
    isImage: false,
    isVideo: true,
    accept: 'video/*',
    fileResult: {
      file: null,
      dataURL: '',
    } as FileResult,
  },
  luggage: {
    title: 'Select your luggage image',
    isImage: true,
    isVideo: false,
    accept: 'image/*,.pdf',
    fileResult: {
      file: null,
      dataURL: '',
    } as FileResult,
  },
  businessCard: {
    title: 'Select your business card',
    isImage: true,
    isVideo: false,
    accept: 'image/*,.pdf',
    fileResult: {
      file: null,
      dataURL: '',
    } as FileResult,
  },
};

const uiStore = namespace('Ui');

@Component({ components: { FileDialog, StatusDialog } })
export default class Home extends Vue {
  dialogTitle = '';
  showModal = false;
  validationReady = false;
  currentData = data.boardingPass;

  get currentDataItem() {
    return this.currentData;
  }

  set currentDataItem(value) {
    this.currentData = value;
  }

  kioskService: KioskService = kioskService;

  data = data;

  @Ref('validationDialog')
  validationDialog: StatusDialog;

  showValidationDialog = false;
  videoStatus = {
    state: 'Processing',
    percentage: '30%',
  };

  @uiStore.Action
  public showToast!: (config: any) => void;

  // async openValidationDialog() {
  //   this.showValidationDialog = true;
  //   this.validationDialog.startVideoUpload();

  //   await new Promise((resolve) => {
  //     const timer = setTimeout(() => {
  //       this.validationDialog.onVideoStatusUpdate(this.videoStatus);
  //       resolve(null);

  //       clearTimeout(timer);
  //     }, 1500);
  //   });
  // }

  onModalClosed() {
    this.showModal = false;
  }

  onValidationModalClosed() {
    this.showValidationDialog = false;
  }

  openModal(dataItem: typeof data.boardingPass) {
    this.currentDataItem = dataItem;
    this.showModal = true;
  }

  onModalResult(result: FileResult) {
    this.currentDataItem.fileResult = result;
    this.showModal = false;
  }

  async validate() {
    if (!(this.data.boardingPass.fileResult.file && this.data.identityDoc.fileResult.file)) {
      this.showToast({
        text: 'Boarding pass file and document identity file are required',
        color: 'error',
      });

      return;
    }

    if (this.data.video.fileResult.file) {
      this.validationDialog.startVideoUpload();
    } else {
      this.validationDialog.onVideoUploadComplete();
    }

    this.showValidationDialog = true;
    this.validationReady = false;

    try {
      const response = await this.kioskService.validate(
        this.data.boardingPass.fileResult.file,
        this.data.identityDoc.fileResult.file,
        this.data.video.fileResult.file,
        this.data.luggage.fileResult.file,
        this.validationDialog.onVideoStatusUpdate,
        this.validationDialog.onVideoUploadComplete
      );

      this.validationDialog.onValidationComplete(response);

      console.log(response);
    } catch (e) {
      this.showToast({
        text: e.toString(),
        color: 'error',
      });

      this.showValidationDialog = false;
    }
  }
}
</script>
