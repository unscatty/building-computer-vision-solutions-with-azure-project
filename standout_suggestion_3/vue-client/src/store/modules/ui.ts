import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators';

const defaultToastConfig = {
  show: false,
  time: 3000,
  text: 'Mensaje de prueba',
  color: 'success',
};

@Module({ namespaced: true })
class Ui extends VuexModule {
  toast = { ...defaultToastConfig };

  @Mutation
  public setToastVisibility(visible: boolean): void {
    this.toast.show = visible;
  }

  @Mutation
  public setToast(config: any): void {
    this.toast = Object.assign(defaultToastConfig, config);
  }

  @Action
  showToast(config: any) {
    const data = config || {};
    data.show = true;
    this.context.commit('setToast', data || {});
  }
}
export default Ui;
