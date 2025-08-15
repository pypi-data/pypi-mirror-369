import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import { d as defineComponent, r as ref, m as watch, c as openBlock, e as createElementBlock, p as createBaseVNode, f as createVNode, w as withCtx, F as Fragment, q as renderList, h as createBlock, u as unref, an as ElOption, ao as ElSelect, _ as _export_sfc, b as resolveComponent, i as createCommentVNode, l as computed, g as createTextVNode, a as axios, n as onMounted, R as nextTick, a7 as Teleport } from "./index-f6c15e76.js";
import { w as warning_filled_default, F as FileBrowser } from "./designer-13eabd83.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-988d9efe.js";
const createDefaultParquetSettings = () => {
  return {
    file_type: "parquet"
  };
};
const createDefaultCsvSettings = () => {
  return {
    delimiter: ",",
    encoding: "utf-8",
    file_type: "csv"
  };
};
const createDefaultExcelSettings = () => {
  return {
    sheet_name: "Sheet1",
    file_type: "excel"
  };
};
const createDefaultOutputSettings = () => {
  return {
    name: "",
    directory: "",
    file_type: "parquet",
    fields: [],
    write_mode: "overwrite",
    output_csv_table: createDefaultCsvSettings(),
    output_parquet_table: createDefaultParquetSettings(),
    output_excel_table: createDefaultExcelSettings()
  };
};
const _hoisted_1$4 = { class: "csv-table-settings" };
const _hoisted_2$2 = { class: "input-group" };
const _hoisted_3$2 = { class: "input-group" };
const _sfc_main$4 = /* @__PURE__ */ defineComponent({
  __name: "outputCsv",
  props: {
    modelValue: {
      type: Object,
      required: true
    }
  },
  emits: ["update:modelValue"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const localCsvTable = ref(props.modelValue);
    const csv_settings = {
      delimiter_options: [",", ";", "|", "tab"],
      encoding_options: ["utf-8", "ISO-8859-1", "ASCII"]
    };
    const updateParent = () => {
      emit("update:modelValue", localCsvTable.value);
    };
    watch(
      () => props.modelValue,
      (newVal) => {
        localCsvTable.value = newVal;
      },
      { deep: true }
    );
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1$4, [
        createBaseVNode("div", _hoisted_2$2, [
          _cache[2] || (_cache[2] = createBaseVNode("label", { for: "delimiter" }, "File delimiter:", -1)),
          createVNode(unref(ElSelect), {
            modelValue: localCsvTable.value.delimiter,
            "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => localCsvTable.value.delimiter = $event),
            placeholder: "Select delimiter",
            size: "small",
            style: { "max-width": "200px" },
            onChange: updateParent
          }, {
            default: withCtx(() => [
              (openBlock(true), createElementBlock(Fragment, null, renderList(csv_settings.delimiter_options, (option) => {
                return openBlock(), createBlock(unref(ElOption), {
                  key: option,
                  label: option,
                  value: option
                }, null, 8, ["label", "value"]);
              }), 128))
            ]),
            _: 1
          }, 8, ["modelValue"])
        ]),
        createBaseVNode("div", _hoisted_3$2, [
          _cache[3] || (_cache[3] = createBaseVNode("label", { for: "encoding" }, "File encoding:", -1)),
          createVNode(unref(ElSelect), {
            modelValue: localCsvTable.value.encoding,
            "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => localCsvTable.value.encoding = $event),
            placeholder: "Select encoding",
            size: "small",
            style: { "max-width": "200px" },
            onChange: updateParent
          }, {
            default: withCtx(() => [
              (openBlock(true), createElementBlock(Fragment, null, renderList(csv_settings.encoding_options, (option) => {
                return openBlock(), createBlock(unref(ElOption), {
                  key: option,
                  label: option,
                  value: option
                }, null, 8, ["label", "value"]);
              }), 128))
            ]),
            _: 1
          }, 8, ["modelValue"])
        ])
      ]);
    };
  }
});
const outputCsv_vue_vue_type_style_index_0_scoped_9ecfb42a_lang = "";
const CsvTableConfig = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["__scopeId", "data-v-9ecfb42a"]]);
const _hoisted_1$3 = { class: "excel-table-settings" };
const _hoisted_2$1 = { class: "mandatory-section" };
const _hoisted_3$1 = {
  key: 0,
  class: "section-divider"
};
const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "outputExcel",
  props: {
    modelValue: {
      type: Object,
      required: true
    }
  },
  emits: ["update:modelValue"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const localExcelTable = ref(props.modelValue);
    const showOptionalSettings = ref(false);
    const updateParent = () => {
      emit("update:modelValue", localExcelTable.value);
    };
    watch(
      () => props.modelValue,
      (newVal) => {
        localExcelTable.value = newVal;
      },
      { deep: true }
    );
    return (_ctx, _cache) => {
      const _component_el_input = resolveComponent("el-input");
      return openBlock(), createElementBlock("div", _hoisted_1$3, [
        createBaseVNode("div", _hoisted_2$1, [
          _cache[1] || (_cache[1] = createBaseVNode("label", { for: "sheet-name" }, "Sheet Name:", -1)),
          createVNode(_component_el_input, {
            id: "sheet-name",
            modelValue: localExcelTable.value.sheet_name,
            "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => localExcelTable.value.sheet_name = $event),
            type: "text",
            required: "",
            size: "small",
            onInput: updateParent
          }, null, 8, ["modelValue"]),
          showOptionalSettings.value ? (openBlock(), createElementBlock("hr", _hoisted_3$1)) : createCommentVNode("", true)
        ])
      ]);
    };
  }
});
const outputExcel_vue_vue_type_style_index_0_scoped_45248953_lang = "";
const ExcelTableConfig = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-45248953"]]);
const _hoisted_1$2 = { class: "parquet-table-settings" };
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "outputParquet",
  props: {
    modelValue: {
      type: Object,
      required: true
    }
  },
  emits: ["update:modelValue"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const localParquetTable = ref(props.modelValue);
    watch(
      () => props.modelValue,
      (newVal) => {
        localParquetTable.value = newVal;
      },
      { deep: true }
    );
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1$2);
    };
  }
});
const outputParquet_vue_vue_type_style_index_0_scoped_7db0128e_lang = "";
const ParquetTableConfig = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-7db0128e"]]);
const _hoisted_1$1 = {
  key: 0,
  class: "listbox-wrapper"
};
const _hoisted_2 = { class: "main-part" };
const _hoisted_3 = { class: "file-upload-row" };
const _hoisted_4 = {
  key: 1,
  class: "warning-message"
};
const _hoisted_5 = { class: "main-part" };
const _hoisted_6 = { class: "file-type-row" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "output",
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const nodeOutput = ref(null);
    const dataLoaded = ref(false);
    const showFileSelectionModal = ref(false);
    const selectedDirectoryExists = ref(null);
    const localFileInfos = ref([]);
    const hasFileExtension = computed(() => {
      var _a, _b;
      return ((_b = (_a = nodeOutput.value) == null ? void 0 : _a.output_settings.name) == null ? void 0 : _b.includes(".")) ?? false;
    });
    function getWriteOptions(fileType) {
      return fileType === "csv" ? ["overwrite", "new file", "append"] : ["overwrite", "new file"];
    }
    async function fetchFiles() {
      var _a, _b;
      try {
        const response = await axios.get("/files/files_in_local_directory/", {
          params: { directory: (_a = nodeOutput.value) == null ? void 0 : _a.output_settings.directory },
          headers: { accept: "application/json" }
        });
        localFileInfos.value = response.data;
        selectedDirectoryExists.value = true;
      } catch (err) {
        const axiosError = err;
        if (((_b = axiosError.response) == null ? void 0 : _b.status) === 404) {
          localFileInfos.value = [];
          selectedDirectoryExists.value = false;
        }
      }
    }
    function detectFileType(fileName) {
      var _a;
      if (!fileName)
        return;
      const extension = (_a = fileName.split(".").pop()) == null ? void 0 : _a.toLowerCase();
      if (!extension || !["csv", "xlsx", "xls", "parquet"].includes(extension)) {
        return;
      }
      const verifiedExtension = extension;
      const fileTypeMap = {
        csv: "csv",
        xlsx: "excel",
        xls: "excel",
        parquet: "parquet"
      };
      if (nodeOutput.value && fileTypeMap[verifiedExtension]) {
        nodeOutput.value.output_settings.file_type = fileTypeMap[verifiedExtension];
        nodeOutput.value.output_settings.write_mode = "overwrite";
      }
    }
    function handleFileNameChange() {
      var _a;
      if ((_a = nodeOutput.value) == null ? void 0 : _a.output_settings.name) {
        detectFileType(nodeOutput.value.output_settings.name);
      }
    }
    function handleFileTypeChange() {
      if (!nodeOutput.value)
        return;
      const fileExtMap = {
        csv: ".csv",
        excel: ".xlsx",
        parquet: ".parquet"
      };
      const baseName = nodeOutput.value.output_settings.name.split(".")[0];
      nodeOutput.value.output_settings.name = baseName + (fileExtMap[nodeOutput.value.output_settings.file_type] || "");
      if (!nodeOutput.value.output_settings.write_mode) {
        nodeOutput.value.output_settings.write_mode = "overwrite";
      }
    }
    function handleDirectorySelected(directoryPath) {
      if (!nodeOutput.value)
        return;
      nodeOutput.value.output_settings.directory = directoryPath;
      showFileSelectionModal.value = false;
      fetchFiles();
    }
    function handleFileSelected(filePath, currentPath, fileName) {
      if (!nodeOutput.value)
        return;
      nodeOutput.value.output_settings.name = fileName;
      nodeOutput.value.output_settings.directory = currentPath;
      showFileSelectionModal.value = false;
      detectFileType(fileName);
    }
    function handleFolderChange() {
      fetchFiles();
    }
    const querySearch = (queryString, cb) => {
      const results = queryString ? localFileInfos.value.filter(
        (item) => item.file_name.toLowerCase().startsWith(queryString.toLowerCase())
      ) : localFileInfos.value;
      cb(results);
    };
    async function loadNodeData(nodeId) {
      const nodeResult = await nodeStore.getNodeData(nodeId, false);
      if ((nodeResult == null ? void 0 : nodeResult.setting_input) && nodeResult.setting_input.is_setup) {
        nodeOutput.value = nodeResult.setting_input;
        console.log("this is all good", nodeResult == null ? void 0 : nodeResult.setting_input);
      } else {
        nodeOutput.value = {
          output_settings: createDefaultOutputSettings(),
          flow_id: nodeStore.flow_id,
          node_id: nodeId,
          cache_results: false,
          pos_x: 0,
          pos_y: 0,
          is_setup: false,
          description: ""
        };
      }
      dataLoaded.value = true;
    }
    async function pushNodeData() {
      var _a;
      if ((_a = nodeOutput.value) == null ? void 0 : _a.output_settings) {
        await nodeStore.updateSettings(nodeOutput);
        dataLoaded.value = false;
      }
    }
    __expose({
      loadNodeData,
      pushNodeData
    });
    return (_ctx, _cache) => {
      const _component_el_input = resolveComponent("el-input");
      const _component_el_icon = resolveComponent("el-icon");
      const _component_el_autocomplete = resolveComponent("el-autocomplete");
      const _component_el_option = resolveComponent("el-option");
      const _component_el_select = resolveComponent("el-select");
      const _component_el_dialog = resolveComponent("el-dialog");
      return dataLoaded.value && nodeOutput.value && nodeOutput.value.output_settings ? (openBlock(), createElementBlock("div", _hoisted_1$1, [
        createBaseVNode("div", _hoisted_2, [
          createBaseVNode("div", _hoisted_3, [
            createBaseVNode("label", {
              class: "file-upload-label",
              onClick: _cache[0] || (_cache[0] = ($event) => showFileSelectionModal.value = true)
            }, _cache[9] || (_cache[9] = [
              createBaseVNode("i", { class: "file-icon fas fa-upload" }, null, -1),
              createBaseVNode("span", { class: "file-label-text" }, "Folder", -1)
            ])),
            nodeOutput.value.output_settings ? (openBlock(), createBlock(_component_el_input, {
              key: 0,
              modelValue: nodeOutput.value.output_settings.directory,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => nodeOutput.value.output_settings.directory = $event),
              size: "small",
              onChange: handleFolderChange
            }, null, 8, ["modelValue"])) : createCommentVNode("", true),
            selectedDirectoryExists.value === false ? (openBlock(), createElementBlock("span", _hoisted_4, [
              createVNode(_component_el_icon, null, {
                default: withCtx(() => [
                  createVNode(unref(warning_filled_default))
                ]),
                _: 1
              })
            ])) : createCommentVNode("", true)
          ]),
          createVNode(_component_el_autocomplete, {
            modelValue: nodeOutput.value.output_settings.name,
            "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => nodeOutput.value.output_settings.name = $event),
            "fetch-suggestions": querySearch,
            clearable: "",
            class: "inline-input w-50",
            placeholder: "Select file or create file",
            "trigger-on-focus": false,
            onChange: handleFileNameChange,
            onSelect: handleFileNameChange
          }, null, 8, ["modelValue"])
        ]),
        createBaseVNode("div", _hoisted_5, [
          createBaseVNode("div", _hoisted_6, [
            _cache[10] || (_cache[10] = createTextVNode(" File type: ")),
            createVNode(_component_el_select, {
              modelValue: nodeOutput.value.output_settings.file_type,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => nodeOutput.value.output_settings.file_type = $event),
              class: "m-2",
              placeholder: "Select",
              size: "small",
              disabled: hasFileExtension.value,
              onChange: handleFileTypeChange
            }, {
              default: withCtx(() => [
                (openBlock(), createElementBlock(Fragment, null, renderList(["csv", "excel", "parquet"], (type) => {
                  return createVNode(_component_el_option, {
                    key: type,
                    label: type,
                    value: type
                  }, null, 8, ["label", "value"]);
                }), 64))
              ]),
              _: 1
            }, 8, ["modelValue", "disabled"])
          ]),
          _cache[11] || (_cache[11] = createTextVNode(" Writing option: ")),
          createVNode(_component_el_select, {
            modelValue: nodeOutput.value.output_settings.write_mode,
            "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => nodeOutput.value.output_settings.write_mode = $event),
            class: "m-2",
            placeholder: "Select output option",
            size: "small",
            disabled: !nodeOutput.value.output_settings.file_type
          }, {
            default: withCtx(() => [
              (openBlock(true), createElementBlock(Fragment, null, renderList(getWriteOptions(nodeOutput.value.output_settings.file_type), (option) => {
                return openBlock(), createBlock(_component_el_option, {
                  key: option,
                  label: option,
                  value: option
                }, null, 8, ["label", "value"]);
              }), 128))
            ]),
            _: 1
          }, 8, ["modelValue", "disabled"]),
          nodeOutput.value.output_settings.file_type === "csv" ? (openBlock(), createBlock(CsvTableConfig, {
            key: 0,
            modelValue: nodeOutput.value.output_settings.output_csv_table,
            "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => nodeOutput.value.output_settings.output_csv_table = $event)
          }, null, 8, ["modelValue"])) : createCommentVNode("", true),
          nodeOutput.value.output_settings.file_type === "excel" ? (openBlock(), createBlock(ExcelTableConfig, {
            key: 1,
            modelValue: nodeOutput.value.output_settings.output_excel_table,
            "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => nodeOutput.value.output_settings.output_excel_table = $event)
          }, null, 8, ["modelValue"])) : createCommentVNode("", true),
          nodeOutput.value.output_settings.file_type === "parquet" ? (openBlock(), createBlock(ParquetTableConfig, {
            key: 2,
            modelValue: nodeOutput.value.output_settings.output_parquet_table,
            "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => nodeOutput.value.output_settings.output_parquet_table = $event)
          }, null, 8, ["modelValue"])) : createCommentVNode("", true)
        ]),
        createVNode(_component_el_dialog, {
          modelValue: showFileSelectionModal.value,
          "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => showFileSelectionModal.value = $event),
          title: "Select directory or file to write to",
          width: "70%"
        }, {
          default: withCtx(() => [
            createVNode(FileBrowser, {
              "allowed-file-types": ["csv", "xlsx", "parquet"],
              "allow-directory-selection": true,
              mode: "create",
              onDirectorySelected: handleDirectorySelected,
              onOverwriteFile: handleFileSelected,
              onCreateFile: handleFileSelected
            })
          ]),
          _: 1
        }, 8, ["modelValue"])
      ])) : createCommentVNode("", true);
    };
  }
});
const output_vue_vue_type_style_index_0_scoped_3955fb0e_lang = "";
const outputPage = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-3955fb0e"]]);
const _hoisted_1 = { ref: "el" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Output",
  props: {
    nodeId: {
      type: Number,
      required: true
    }
  },
  setup(__props) {
    const props = __props;
    const nodeStore = useNodeStore();
    ref(false);
    const childComp = ref(null);
    const closeOnDrawer = () => {
      var _a;
      console.log("closeOnDrawer");
      if (drawer.value) {
        (_a = childComp.value) == null ? void 0 : _a.pushNodeData();
        drawer.value = false;
      }
    };
    const drawer = ref(false);
    const openDrawer = async () => {
      if (nodeStore.node_id === props.nodeId) {
        return;
      }
      nodeStore.closeDrawer();
      drawer.value = true;
      const drawerOpen = nodeStore.isDrawerOpen;
      nodeStore.isDrawerOpen = true;
      await nextTick();
      if (nodeStore.node_id === props.nodeId && drawerOpen) {
        return;
      }
      if (childComp.value) {
        childComp.value.loadNodeData(props.nodeId);
        nodeStore.openDrawer(closeOnDrawer);
      }
    };
    onMounted(async () => {
      await nextTick();
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(NodeButton, {
          ref: "nodeButton",
          "node-id": __props.nodeId,
          "image-src": "output.png",
          title: `${__props.nodeId}: Write data`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Write data",
            intro: "Write data to a file or database"
          }),
          createVNode(outputPage, {
            ref_key: "childComp",
            ref: childComp,
            "node-id": __props.nodeId
          }, null, 8, ["node-id"])
        ])) : createCommentVNode("", true)
      ], 512);
    };
  }
});
export {
  _sfc_main as default
};
