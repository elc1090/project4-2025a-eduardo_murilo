<template>
  <div class="component-upload-form">
    <q-form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Component Details -->
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <h3 class="text-xl font-semibold mb-4">Component Details</h3>

        <q-input
          v-model="formData.title"
          label="Component Title *"
          outlined
          :rules="[(val) => !!val || 'Title is required']"
          class="mb-4"
        />

        <q-input
          v-model="formData.description"
          label="Description"
          outlined
          type="textarea"
          class="mb-4"
        />

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <q-select
            v-model="formData.framework"
            label="Framework *"
            outlined
            :options="frameworkOptions"
            :rules="[(val) => !!val || 'Framework is required']"
          />

          <q-select
            v-model="formData.category"
            label="Category *"
            outlined
            :options="categoryOptions"
            :rules="[(val) => !!val || 'Category is required']"
          />
        </div>

        <q-input
          v-model="formData.tags"
          label="Tags"
          outlined
          hint="Separate tags with commas"
        >
          <template v-slot:after>
            <q-btn
              round
              dense
              flat
              icon="add"
              @click="addTag"
              title="Add tag"
            />
          </template>
        </q-input>

        <div class="flex flex-wrap gap-2 mt-2">
          <q-chip
            v-for="(tag, index) in formData.tagsArray"
            :key="index"
            removable
            @remove="removeTag(index)"
          >
            {{ tag }}
          </q-chip>
        </div>
      </div>

      <!-- Code Editor Section -->
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <h3 class="text-xl font-semibold mb-4">Component Code</h3>

        <div class="mb-4">
          <q-radio v-model="formData.inputType" val="html" label="HTML" />
          <q-radio
            v-model="formData.inputType"
            val="vue"
            label="Vue SFC"
            class="ml-4"
          />
        </div>

        <div
          class="editor-container border border-gray-200 rounded-lg overflow-hidden"
        >
          <div
            class="editor-toolbar bg-gray-100 px-4 py-2 flex justify-between items-center"
          >
            <span class="text-sm font-medium">Component Code *</span>
            <div class="flex items-center space-x-2">
              <q-btn
                flat
                dense
                icon="auto_fix_high"
                label="Auto-preencher"
                @click="autoFillFromCode"
                :disabled="!canAutoFill"
                :loading="isAutoFilling"
                size="sm"
                color="primary"
                title="Gerar informações automaticamente a partir do código"
              />
              <q-btn
                flat
                dense
                icon="content_copy"
                label="Copy"
                @click="copyToClipboard"
                size="sm"
              />
            </div>
          </div>
          <MonacoEditor
            v-model="formData.code"
            :language="formData.inputType === 'vue' ? 'vue' : 'html'"
            height="300px"
            theme="vs"
            class="code-editor"
          />
        </div>

        <q-checkbox
          v-model="formData.includeTailwind"
          label="Include Tailwind CSS"
          class="mt-4"
        />

        <!-- Temporarily disabled Quasar option -->
        <!--
        <q-checkbox
          v-model="formData.includeQuasar"
          label="Include Quasar Framework"
          class="mt-2"
        />
        -->
      </div>

      <!-- Preview Section -->
      <div class="bg-white p-6 rounded-lg shadow-sm">
        <h3 class="text-xl font-semibold mb-4">Live Preview</h3>
        <ComponentViewer
          :content="formData.code"
          :framework="formData.inputType === 'vue' ? 'vue' : 'html'"
          :include-tailwind="formData.includeTailwind"
          :include-quasar="formData.includeQuasar"
        />
      </div>

      <!-- Actions -->
      <div class="flex justify-end space-x-4">
        <q-btn
          label="Reset"
          type="reset"
          color="grey"
          flat
          @click="resetForm"
        />
        <q-btn
          :label="props.isEditMode ? 'Update Component' : 'Upload Component'"
          type="submit"
          color="primary"
          :loading="isSubmitting"
        />
      </div>
    </q-form>

    <!-- Auto-fill confirmation dialog -->
    <q-dialog v-model="showAutoFillDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Informações Detectadas</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <div class="text-body2 text-grey-7 q-mb-md">
            As seguintes informações foram detectadas automaticamente no seu
            código:
          </div>

          <div v-if="autoFillData" class="q-gutter-sm">
            <div v-if="autoFillData.title" class="row">
              <div class="col-4 text-weight-medium">Título:</div>
              <div class="col-8">{{ autoFillData.title }}</div>
            </div>

            <div v-if="autoFillData.description" class="row">
              <div class="col-4 text-weight-medium">Descrição:</div>
              <div class="col-8">{{ autoFillData.description }}</div>
            </div>

            <div v-if="autoFillData.framework" class="row">
              <div class="col-4 text-weight-medium">Framework:</div>
              <div class="col-8">{{ autoFillData.framework }}</div>
            </div>

            <div v-if="autoFillData.category" class="row">
              <div class="col-4 text-weight-medium">Categoria:</div>
              <div class="col-8">{{ autoFillData.category }}</div>
            </div>

            <div v-if="autoFillData.tags" class="row">
              <div class="col-4 text-weight-medium">Tags:</div>
              <div class="col-8">
                <q-chip
                  v-for="tag in typeof autoFillData.tags === 'string'
                    ? autoFillData.tags.split(',')
                    : autoFillData.tags"
                  :key="tag"
                  size="sm"
                  color="primary"
                  text-color="white"
                >
                  {{ tag.trim() }}
                </q-chip>
              </div>
            </div>

            <div v-if="autoFillData.inputType" class="row">
              <div class="col-4 text-weight-medium">Tipo:</div>
              <div class="col-8">{{ autoFillData.inputType }}</div>
            </div>

            <div
              v-if="typeof autoFillData.includeTailwind === 'boolean'"
              class="row"
            >
              <div class="col-4 text-weight-medium">Tailwind CSS:</div>
              <div class="col-8">
                <q-icon
                  :name="
                    autoFillData.includeTailwind ? 'check_circle' : 'cancel'
                  "
                  :color="
                    autoFillData.includeTailwind ? 'positive' : 'negative'
                  "
                />
                {{ autoFillData.includeTailwind ? "Sim" : "Não" }}
              </div>
            </div>
          </div>

          <q-banner
            v-if="hasExistingData"
            class="bg-orange-1 text-orange-8 q-mt-md"
            rounded
          >
            <template v-slot:avatar>
              <q-icon name="warning" color="orange" />
            </template>
            Alguns campos já possuem dados. Confirmar irá sobrescrever as
            informações existentes.
          </q-banner>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="grey" v-close-popup />
          <q-btn
            label="Confirmar e Aplicar"
            color="primary"
            @click="applyAutoFillData"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted } from "vue";
import { useQuasar } from "quasar";
import { useRouter } from "vue-router";
import ComponentViewer from "./ComponentViewer.vue";
import MonacoEditor from "./MonacoEditor.vue";
import {
  saveComponent,
  getComponentInfo,
  updateComponent,
} from "src/services/DefaultService";
import { useAuthStore } from "stores/auth";

// Props
const props = defineProps({
  componentData: {
    type: Object,
    default: null,
  },
  isEditMode: {
    type: Boolean,
    default: false,
  },
  componentId: {
    type: [String, Number],
    default: null,
  },
});

const $q = useQuasar();
const auth = useAuthStore();
const router = useRouter();

const formData = ref({
  title: "",
  description: "",
  framework: "vue",
  category: "ui",
  tags: "",
  tagsArray: [],
  code: `<template>
  <div class="p-6 bg-white rounded-lg shadow-lg border border-gray-200">
    <h2 class="text-2xl font-bold text-gray-800 mb-3">{{ title }}</h2>
    <p class="text-gray-600 mb-4">{{ description }}</p>

    <button
      @click="handleClick"
      class="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    >
      Click Me
    </button>

    <div
      v-if="clicked"
      class="mt-4 inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium animate-pulse border border-green-200"
    >
      ✅ Button clicked successfully!
    </div>

    <div class="mt-4 flex items-center justify-between">
      <div class="text-sm text-gray-500">
        Count: <span class="font-semibold text-gray-700">{{ clickCount }}</span>
      </div>
      <button
        v-if="clickCount > 0"
        @click="resetCount"
        class="text-xs text-red-500 hover:text-red-700 underline"
      >
        Reset
      </button>
    </div>

    <div v-if="clickCount >= 5" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
      <p class="text-sm text-yellow-800">
        🎉 Wow! You've clicked {{ clickCount }} times! You're really testing this component!
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Reactive data
const title = ref('New Component')
const description = ref('Edit this code to create your component with Vue 3 + Tailwind')
const clicked = ref(false)
const clickCount = ref(0)

// Computed properties
const isActive = computed(() => clickCount.value > 0)

// Methods
const handleClick = () => {
  clicked.value = true
  clickCount.value++

  console.log('Button clicked! Count:', clickCount.value)

  // Reset the clicked state after 3 seconds
  setTimeout(() => {
    clicked.value = false
  }, 3000)
}

const resetCount = () => {
  clickCount.value = 0
  clicked.value = false
  console.log('Count reset!')
}

// Lifecycle
onMounted(() => {
  console.log('Component mounted with Vue 3 Composition API!')
})
<\/script>`,
  inputType: "vue",
  includeTailwind: true,
  includeQuasar: false,
});

const frameworkOptions = [
  { label: "Vue 3", value: "vue" },
  { label: "React", value: "react" },
  { label: "HTML/CSS/JS", value: "html" },
];

const categoryOptions = [
  { label: "UI Elements", value: "ui" },
  { label: "Forms", value: "forms" },
  { label: "Navigation", value: "navigation" },
  { label: "Cards", value: "cards" },
  { label: "Data Display", value: "data" },
  { label: "Layout", value: "layout" },
];

const isSubmitting = ref(false);
const isAutoFilling = ref(false);
const showAutoFillDialog = ref(false);
const autoFillData = ref(null);

// Computed property to check if auto-fill button should be enabled
const canAutoFill = computed(() => {
  return formData.value.code.trim().length > 50; // Minimum code length for meaningful analysis
});

// Computed property to check if form has existing data that would be overwritten
const hasExistingData = computed(() => {
  return !!(
    formData.value.title.trim() ||
    formData.value.description.trim() ||
    formData.value.tagsArray.length > 0
  );
});

const addTag = () => {
  if (formData.value.tags.trim()) {
    const newTags = formData.value.tags
      .split(",")
      .map((tag) => tag.trim())
      .filter((tag) => tag && !formData.value.tagsArray.includes(tag));

    formData.value.tagsArray = [...formData.value.tagsArray, ...newTags];
    formData.value.tags = "";
  }
};

const removeTag = (index) => {
  formData.value.tagsArray.splice(index, 1);
};

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(formData.value.code);
    $q.notify({
      type: "positive",
      message: "Code copied to clipboard!",
    });
  } catch (err) {
    $q.notify({
      type: "negative",
      message: "Failed to copy code",
    });
  }
};

const autoFillFromCode = async () => {
  if (!canAutoFill.value) {
    $q.notify({
      type: "warning",
      message: "Adicione mais código para usar o auto-preenchimento",
    });
    return;
  }

  isAutoFilling.value = true;

  try {
    const response = await getComponentInfo(formData.value.code);
    autoFillData.value = response.data;
    showAutoFillDialog.value = true;
  } catch (error) {
    console.error("Error getting component info:", error);
    $q.notify({
      type: "negative",
      message: "Erro ao analisar o código. Tente novamente.",
    });
  } finally {
    isAutoFilling.value = false;
  }
};

const applyAutoFillData = () => {
  if (!autoFillData.value) return;

  const data = autoFillData.value;

  // Apply the auto-filled data to form
  if (data.title) formData.value.title = data.title;
  if (data.description) formData.value.description = data.description;
  if (data.framework) {
    // Find matching framework option
    const frameworkOption = frameworkOptions.find(
      (opt) =>
        opt.value === data.framework.toLowerCase() ||
        opt.label.toLowerCase().includes(data.framework.toLowerCase())
    );
    if (frameworkOption) {
      formData.value.framework = frameworkOption.value;
    }
  }
  if (data.category) {
    // Find matching category option
    const categoryOption = categoryOptions.find(
      (opt) =>
        opt.value === data.category.toLowerCase() ||
        opt.label.toLowerCase().includes(data.category.toLowerCase())
    );
    if (categoryOption) {
      formData.value.category = categoryOption.value;
    }
  }
  if (data.tags) {
    // Handle tags - convert string to array
    const tagsArray =
      typeof data.tags === "string"
        ? data.tags
            .split(",")
            .map((tag) => tag.trim())
            .filter((tag) => tag)
        : data.tags;
    formData.value.tagsArray = [
      ...new Set([...formData.value.tagsArray, ...tagsArray]),
    ];
  }
  if (data.inputType) {
    formData.value.inputType =
      data.inputType.toLowerCase() === "vue sfc" ? "vue" : "html";
  }
  if (typeof data.includeTailwind === "boolean") {
    formData.value.includeTailwind = data.includeTailwind;
  }

  showAutoFillDialog.value = false;

  $q.notify({
    type: "positive",
    message: "Informações preenchidas automaticamente!",
  });
};

const validateForm = () => {
  const errors = [];

  if (!formData.value.title.trim()) {
    errors.push("Component title is required");
  }

  if (!formData.value.framework) {
    errors.push("Framework selection is required");
  }

  if (!formData.value.category) {
    errors.push("Category selection is required");
  }

  if (!formData.value.code.trim()) {
    errors.push("Component code is required");
  }

  return errors;
};

const resetForm = () => {
  formData.value = {
    title: "",
    description: "",
    framework: "vue",
    category: "ui",
    tags: "",
    tagsArray: [],
    code: `<template>
  <div class="p-6 bg-white rounded-lg shadow-lg border border-gray-200">
    <h2 class="text-2xl font-bold text-gray-800 mb-3">{{ title }}</h2>
    <p class="text-gray-600 mb-4">{{ description }}</p>

    <button
      @click="handleClick"
      class="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    >
      Click Me
    </button>

    <div
      v-if="clicked"
      class="mt-4 inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium animate-pulse border border-green-200"
    >
      ✅ Button clicked successfully!
    </div>

    <div class="mt-4 flex items-center justify-between">
      <div class="text-sm text-gray-500">
        Count: <span class="font-semibold text-gray-700">{{ clickCount }}</span>
      </div>
      <button
        v-if="clickCount > 0"
        @click="resetCount"
        class="text-xs text-red-500 hover:text-red-700 underline"
      >
        Reset
      </button>
    </div>

    <div v-if="clickCount >= 5" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
      <p class="text-sm text-yellow-800">
        🎉 Wow! You've clicked {{ clickCount }} times! You're really testing this component!
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Reactive data
const title = ref('New Component')
const description = ref('Edit this code to create your component with Vue 3 + Tailwind')
const clicked = ref(false)
const clickCount = ref(0)

// Computed properties
const isActive = computed(() => clickCount.value > 0)

// Methods
const handleClick = () => {
  clicked.value = true
  clickCount.value++

  console.log('Button clicked! Count:', clickCount.value)

  // Reset the clicked state after 3 seconds
  setTimeout(() => {
    clicked.value = false
  }, 3000)
}

const resetCount = () => {
  clickCount.value = 0
  clicked.value = false
  console.log('Count reset!')
}

// Lifecycle
onMounted(() => {
  console.log('Component mounted with Vue 3 Composition API!')
})
<\/script>`,
    inputType: "vue",
    includeTailwind: true,
    includeQuasar: false,
  };
};

// Load component data when in edit mode
const loadComponentData = () => {
  if (props.componentData) {
    formData.value = {
      title: props.componentData.title || "",
      description: props.componentData.description || "",
      framework: props.componentData.framework || "vue",
      category: props.componentData.category || "ui",
      tags: "",
      tagsArray: Array.isArray(props.componentData.tags)
        ? props.componentData.tags
        : props.componentData.tags
        ? props.componentData.tags.split(",").map((t) => t.trim())
        : [],
      code: props.componentData.code || "",
      inputType: props.componentData.inputType || "vue",
      includeTailwind: props.componentData.includeTailwind !== false,
      includeQuasar: props.componentData.includeQuasar || false,
    };
  }
};

const handleSubmit = async () => {
  // Validate form before submitting
  const validationErrors = validateForm();
  if (validationErrors.length > 0) {
    $q.notify({
      type: "negative",
      message: validationErrors.join(", "),
      position: "top",
    });
    return;
  }

  isSubmitting.value = true;

  try {
    // Prepare the payload for the backend
    const payload = {
      title: formData.value.title,
      description: formData.value.description,
      framework: formData.value.framework.value || formData.value.framework,
      category: formData.value.category.value || formData.value.category,
      tags: formData.value.tagsArray,
      code: formData.value.code,
      inputType: formData.value.inputType,
      includeTailwind: formData.value.includeTailwind,
      includeQuasar: formData.value.includeQuasar,
    };

    // Add user_id only for new components
    if (!props.isEditMode) {
      payload.user_id = auth.authData.user.id;
    }

    console.log("Sending payload to backend:", payload);

    // Call the appropriate API based on mode
    const response = props.isEditMode
      ? await updateComponent(props.componentId, payload)
      : await saveComponent(payload);

    console.log("Component saved successfully:", response.data);

    // Show success message
    $q.notify({
      type: "positive",
      message: props.isEditMode
        ? "Component updated successfully!"
        : "Component uploaded successfully!",
      position: "top",
    });

    // Navigate back to dashboard or component view
    if (props.isEditMode) {
      router.push(`/components/${props.componentId}`);
    } else {
      // Reset the form after successful upload
      resetForm();
    }
  } catch (error) {
    console.error("Error saving component:", error);

    // Show error message
    $q.notify({
      type: "negative",
      message:
        error.response?.data?.message ||
        `Failed to ${
          props.isEditMode ? "update" : "upload"
        } component. Please try again.`,
      position: "top",
    });
  } finally {
    isSubmitting.value = false;
  }
};

// Watch for tag input changes to add tags on comma
watch(
  () => formData.value.tags,
  (newVal) => {
    if (newVal.endsWith(",")) {
      addTag();
    }
  }
);

// Watch for input type changes to update the editor language
watch(
  () => formData.value.inputType,
  () => {
    // The language will be updated automatically through the :language binding
    // This watch is here in case we need to add more logic in the future
  }
);

// Watch for component data changes (when props change)
watch(
  () => props.componentData,
  () => {
    if (props.componentData) {
      loadComponentData();
    }
  },
  { immediate: true }
);

// Load component data on mount if in edit mode
onMounted(() => {
  if (props.isEditMode && props.componentData) {
    loadComponentData();
  }
});
</script>

<style scoped>
.editor-container {
  transition: all 0.2s ease;
}

.code-editor {
  width: 100%;
  border-radius: 4px;
  overflow: hidden;
}

:deep(.monaco-editor) {
  border-radius: 4px;
  padding: 0;
}
</style>
