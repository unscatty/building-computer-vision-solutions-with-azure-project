<template>
  <v-dialog v-model="show" max-width="750">
    <v-card>
      <v-card-title>{{ title }}</v-card-title>
      <v-card-text>
        <v-img
          v-show="
            isImage &&
            selectedFile &&
            selectedFile.dataURL &&
            extension(selectedFile.dataURL) !== '.pdf'
          "
          :src="selectedFile ? selectedFile.dataURL : ''"
          alt=""
        />
        <video
          v-show="isVideo && selectedFile && selectedFile.dataURL"
          :src="selectedFile ? selectedFile.dataURL : ''"
          controls
          class="video"
        ></video>
      </v-card-text>
      <v-card-actions>
        <v-btn color="secondary darken-1" text @click="cancel">Cancel</v-btn>
        <!-- <span v-if="filename">{{ filename }}</span>
        <br /> -->
        <v-spacer></v-spacer>
        <input ref="uploader" class="d-none" type="file" :accept="accept" @change="onFileChanged" />
        <v-btn color="success" @click="selectFile"
          ><v-icon left> mdi-cloud-upload </v-icon
          >{{
            (selectedFile && selectedFile.file && selectedFile.file.name) || 'Select a file'
          }}</v-btn
        >
        <v-btn color="secondary darken-1" text @click="upload">OK</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator';
import { extension } from '@/utils/text.util';
import { FileResult } from '@/utils/file.util';

@Component
export default class FileDialog extends Vue {
  @Prop({ type: String, required: false, default: 'Select a file' })
  title: string;

  @Prop({ default: false })
  showDialog: boolean;

  @Prop({ default: false })
  isImage: boolean;

  @Prop({ default: false })
  isVideo: boolean;

  @Prop({ type: String, required: false, default: 'image/*,.pdf' })
  accept: string;

  @Prop({ type: Object, required: false, default: { file: null, dataURL: '' } })
  selectedFile: FileResult = {
    file: null,
    dataURL: '',
  };

  extension = extension;

  get show() {
    return this.showDialog;
  }

  set show(value) {
    if (!value) {
      this.close();
    }
  }

  reset() {
    this.selectedFile = {
      file: null,
      dataURL: '',
    };
  }

  cancel() {
    this.reset();
    this.show = false;
  }

  @Emit()
  close() {
    return;
  }

  @Emit()
  selected(result: FileResult) {
    return result;
  }

  upload() {
    return this.selected(this.selectedFile);
  }

  selectFile() {
    const uploaderRef = this.$refs.uploader as any;
    uploaderRef.click();
  }

  onFileChanged(e: Event) {
    const { files } = e.target as HTMLInputElement;

    if (files && files[0]) {
      const selectedFile = files[0];

      this.selectedFile.file = selectedFile;
      this.selectedFile.dataURL = URL.createObjectURL(selectedFile);
    }
  }
}
</script>

<style lang="scss" scoped>
.video {
  max-width: min-content;
  max-height: min-content;

  @supports (max-width: -moz-available) {
    max-width: -moz-available;
  }

  @supports (max-height: -moz-available) {
    max-height: -moz-available;
  }

  @supports (max-width: -webkit-fill-available) {
    max-width: -webkit-fill-available;
  }

  @supports (max-height: -webkit-fill-available) {
    max-height: -webkit-fill-available;
  }
}
</style>
