import { defineNuxtPlugin } from '#app'
import PrimeVue from 'primevue/config'
import Toast from 'primevue/toast'
import ToastService from 'primevue/toastservice'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import InputSwitch from 'primevue/inputswitch'
import TextArea from 'primevue/textarea'
import FileUpload from 'primevue/fileupload'
import Message from 'primevue/message'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import DynamicDialog from 'primevue/dynamicdialog'
import DialogService from 'primevue/dialogservice'
import ContextMenu from 'primevue/contextmenu'
import Toolbar from 'primevue/toolbar'
import ConfirmDialog from 'primevue/confirmdialog'
import ConfirmationService from 'primevue/confirmationservice'
import OrderList from 'primevue/orderlist'
import Chips from 'primevue/chips'
import Chip from 'primevue/chip'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Fieldset from 'primevue/fieldset'
import Card from 'primevue/card'
import Menubar from 'primevue/menubar'
import ScrollPanel from 'primevue/scrollpanel'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import Badge from 'primevue/badge'
import Tooltip from 'primevue/tooltip'


export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(PrimeVue, { ripple: true })
  nuxtApp.vueApp.use(ToastService)
  nuxtApp.vueApp.use(DialogService)
  nuxtApp.vueApp.use(ConfirmationService)
  nuxtApp.vueApp.directive('Tooltip', Tooltip)
  nuxtApp.vueApp.component('Toast', Toast)
  nuxtApp.vueApp.component('InputText', InputText)
  nuxtApp.vueApp.component('InputNumber', InputNumber)
  nuxtApp.vueApp.component('InputSwitch', InputSwitch)
  nuxtApp.vueApp.component('TextArea', TextArea)
  nuxtApp.vueApp.component('FileUpload', FileUpload)
  nuxtApp.vueApp.component('Message', Message)
  nuxtApp.vueApp.component('Button', Button)
  nuxtApp.vueApp.component('DataTable', DataTable)
  nuxtApp.vueApp.component('Column', Column)
  nuxtApp.vueApp.component('DynamicDialog', DynamicDialog)
  nuxtApp.vueApp.component('ContextMenu', ContextMenu)
  nuxtApp.vueApp.component('Toolbar', Toolbar)
  nuxtApp.vueApp.component('ConfirmDialog', ConfirmDialog)
  nuxtApp.vueApp.component('OrderList', OrderList)
  nuxtApp.vueApp.component('Chips', Chips)
  nuxtApp.vueApp.component('Chip', Chip)
  nuxtApp.vueApp.component('TabView', TabView)
  nuxtApp.vueApp.component('TabPanel', TabPanel)
  nuxtApp.vueApp.component('Fieldset', Fieldset)
  nuxtApp.vueApp.component('Card', Card)
  nuxtApp.vueApp.component('Menubar', Menubar)
  nuxtApp.vueApp.component('ScrollPanel', ScrollPanel)
  nuxtApp.vueApp.component('Dropdown', Dropdown)
  nuxtApp.vueApp.component('MultiSelect', MultiSelect)
  nuxtApp.vueApp.component('Badge', Badge)
  })
