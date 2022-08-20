<template>
  <v-dialog v-model="show" max-width="750">
    <v-card>
      <v-card-title>Validation result</v-card-title>
      <v-card-text>
        <div v-show="!validationReady">
          <span class="text-body-1"> We are verifying your information </span>
          <br />
          <br />
          <span v-show="info" class="text-caption">{{ info }}</span>
          <v-progress-linear v-show="isUploadingVideo" v-model="videoPercentage" height="25">
            <strong>{{ videoPercentage }}%</strong>
          </v-progress-linear>
          <v-progress-linear v-show="!isUploadingVideo" indeterminate height="25">
          </v-progress-linear>
        </div>
        <v-alert v-show="validationReady" text :color="messageColor">
          <!-- <h3 class="text-h5">{{ validationHint }}</h3> -->
          <div style="white-space: pre-line">
            {{ validationMessage }}
          </div>
          <br />

          <v-row align="center" no-gutters>
            <v-spacer></v-spacer>
            <v-col class="shrink">
              <v-btn :color="messageColor" outlined @click="close"> Okay </v-btn>
            </v-col>
          </v-row>
        </v-alert>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator';

@Component
export default class StatusDialog extends Vue {
  @Prop({ default: false })
  showDialog: boolean;

  @Prop({ default: false })
  validationReady = false;

  isUploadingVideo = true;
  isBoardingValid = false;

  videoStatus = {
    state: '',
    percentage: '0%',
  };

  validationResult: {
    [key: string]: {
      valid: boolean;
      response: any;
    };
  };

  info = '';
  // validationHint = '';
  validationMessage = '';
  messageColor = 'info';

  startVideoUpload() {
    this.isUploadingVideo = true;
    this.info = 'Uploading and analyzing your video';
  }

  onVideoStatusUpdate(videoStatus: typeof StatusDialog.prototype.videoStatus) {
    this.videoStatus = videoStatus;
  }

  onVideoUploadComplete() {
    this.isUploadingVideo = false;
    this.info = 'Validating your documents';
  }

  onValidationComplete(result: typeof StatusDialog.prototype.validationResult) {
    let resultMessage = '';

    this.messageColor = 'error';
    this.isBoardingValid = false;

    if (result.boardingPass?.valid) {
      if (result.idDocument?.valid) {
        resultMessage = `
          Dear ${
            result.idDocument.response?.sex?.value === 'M'
              ? 'Mr.'
              : result.idDocument.response?.sex?.value === 'F'
              ? 'Mrs.'
              : ''
          } ${result.boardingPass.response?.passengerName?.value},
          You are welcome to flight #${
            result.boardingPass.response?.flightNumber?.value
          } leaving at ${result.boardingPass.response?.boardingTime?.value} from ${
          result.boardingPass.response?.from?.value
        } to ${result.boardingPass.response?.to?.value}.
          Your seat number is ${result.boardingPass.response?.seat?.value}, and it is confirmed.
          Your boarding gate is ${result.boardingPass.response?.gate?.value}
        `;
        if (result.luggage) {
          if (result.luggage?.valid) {
            resultMessage += `
          We did not find a prohibited item (lighter) in your carry-on baggage, thanks for following the procedure.
          `;
            this.messageColor = 'success';
            this.isBoardingValid = true;
          } else {
            resultMessage += `
          We have found a prohibited item (lighter) in your carry-on baggage, and it is flagged for removal.
          `;
          }
        } else {
          resultMessage += `
          We couldn't verify your luggage. Please see a customer service representative.
          `;

          this.messageColor = 'warning';
        }
      } else {
        resultMessage = `
        Dear Sir/Madam,
        Some of the information on your ID card does not match the flight manifest data, so you cannot board the plane.
        Please see a customer service representative.
        `;
      }
    } else {
      resultMessage = `
      Dear Sir/Madam,
      Some of the information in your boarding pass does not match the flight manifest data, so you cannot board the plane.
      Please see a customer service representative.
      `;
    }

    if (result.identity?.valid) {
      if (result.luggage?.valid && this.isBoardingValid) {
        resultMessage += `
        Your identity is verified so please board the plane.
        `;
      } else {
        resultMessage += `
        Your identity is verified. However, your baggage verification failed, so please see a customer service representative.
        `;

        this.messageColor = 'error';
        this.isBoardingValid = false;
      }
    } else {
      if (this.messageColor != 'error') this.messageColor = 'warning';

      resultMessage += `
      Your identity could not be verified. Please see a customer service representative.
      `;
    }

    this.validationMessage = resultMessage;
    // Show validation message
    this.validationReady = true;
  }

  get videoPercentage() {
    return parseInt(this.videoStatus.percentage.replace('%', ''));
  }

  get show() {
    return this.showDialog;
  }

  set show(value) {
    if (!value) {
      this.close();
    }
  }

  @Emit()
  close() {
    return;
  }
}
</script>
