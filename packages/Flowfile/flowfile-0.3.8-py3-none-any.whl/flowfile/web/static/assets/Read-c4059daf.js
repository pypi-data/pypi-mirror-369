import { C as CodeLoader } from "./vue-content-loader.es-0371da73.js";
import { a as axios, d as defineComponent, r as ref, l as computed, n as onMounted, m as watch, b as resolveComponent, c as openBlock, e as createElementBlock, p as createBaseVNode, f as createVNode, w as withCtx, i as createCommentVNode, t as toDisplayString, a5 as withDirectives, a6 as vModelText, h as createBlock, u as unref, _ as _export_sfc, ar as ElCheckbox, F as Fragment, q as renderList, an as ElOption, ao as ElSelect, as as ElSlider, R as nextTick, a7 as Teleport } from "./index-f6c15e76.js";
import { C as ColumnSelector } from "./dropDown-13564764.js";
import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import { F as FileBrowser } from "./designer-13eabd83.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-988d9efe.js";
const getXlsxSheetNamesForPath = async (path) => {
  const response = await axios.get(`/api/get_xlsx_sheet_names?path=${path}`);
  return response.data;
};
const _hoisted_1$3 = { key: 0 };
const _hoisted_2$2 = { class: "table" };
const _hoisted_3$2 = {
  key: 0,
  class: "selectors"
};
const _hoisted_4$2 = { class: "row" };
const _hoisted_5$2 = { class: "input-wrapper" };
const _hoisted_6$2 = {
  key: 0,
  class: "warning-sign"
};
const _hoisted_7$2 = { class: "row" };
const _hoisted_8$1 = { class: "button-container" };
const _hoisted_9$1 = {
  key: 0,
  class: "optional-section"
};
const _hoisted_10 = { class: "row" };
const _hoisted_11 = { class: "input-wrapper" };
const _hoisted_12 = { class: "input-wrapper" };
const _hoisted_13 = { class: "row" };
const _hoisted_14 = { class: "input-wrapper" };
const _hoisted_15 = { class: "input-wrapper" };
const _sfc_main$4 = /* @__PURE__ */ defineComponent({
  __name: "readExcel",
  props: {
    modelValue: {
      type: Object,
      required: true
    }
  },
  emits: ["update:modelValue"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const isLoaded = ref(false);
    const emit = __emit;
    const localExcelTable = ref({ ...props.modelValue });
    const showOptionalSettings = ref(false);
    const sheetNames = ref([]);
    const sheetNamesLoaded = ref(false);
    const getSheetNames = async () => {
      sheetNames.value = await getXlsxSheetNamesForPath(localExcelTable.value.path);
      sheetNamesLoaded.value = true;
    };
    const toggleOptionalSettings = () => {
      showOptionalSettings.value = !showOptionalSettings.value;
    };
    const showWarning = computed(() => {
      if (!sheetNamesLoaded.value) {
        return false;
      }
      return !sheetNames.value.includes(localExcelTable.value.sheet_name);
    });
    onMounted(() => {
      if (localExcelTable.value.path) {
        getSheetNames();
      }
      isLoaded.value = true;
    });
    watch(
      () => localExcelTable.value,
      (newValue) => {
        emit("update:modelValue", { ...newValue });
      },
      { deep: true }
    );
    return (_ctx, _cache) => {
      const _component_el_row = resolveComponent("el-row");
      const _component_el_checkbox = resolveComponent("el-checkbox");
      return isLoaded.value ? (openBlock(), createElementBlock("div", _hoisted_1$3, [
        createBaseVNode("div", _hoisted_2$2, [
          localExcelTable.value ? (openBlock(), createElementBlock("div", _hoisted_3$2, [
            createBaseVNode("div", _hoisted_4$2, [
              createVNode(_component_el_row, null, {
                default: withCtx(() => [
                  createBaseVNode("div", _hoisted_5$2, [
                    _cache[7] || (_cache[7] = createBaseVNode("label", null, "Sheet Name", -1)),
                    createVNode(ColumnSelector, {
                      modelValue: localExcelTable.value.sheet_name,
                      "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => localExcelTable.value.sheet_name = $event),
                      placeholder: "Select or type sheet name",
                      "column-options": sheetNames.value,
                      "is-loading": !sheetNamesLoaded.value
                    }, null, 8, ["modelValue", "column-options", "is-loading"]),
                    showWarning.value ? (openBlock(), createElementBlock("span", _hoisted_6$2, "⚠️")) : createCommentVNode("", true)
                  ])
                ]),
                _: 1
              })
            ]),
            createBaseVNode("div", _hoisted_7$2, [
              createVNode(_component_el_checkbox, {
                modelValue: localExcelTable.value.has_headers,
                "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => localExcelTable.value.has_headers = $event),
                label: "Has headers",
                size: "large"
              }, null, 8, ["modelValue"]),
              createVNode(_component_el_checkbox, {
                modelValue: localExcelTable.value.type_inference,
                "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => localExcelTable.value.type_inference = $event),
                label: "Type inference",
                size: "large"
              }, null, 8, ["modelValue"])
            ]),
            _cache[15] || (_cache[15] = createBaseVNode("hr", { class: "section-divider" }, null, -1)),
            createBaseVNode("div", _hoisted_8$1, [
              createBaseVNode("button", {
                class: "toggle-button",
                onClick: toggleOptionalSettings
              }, toDisplayString(showOptionalSettings.value ? "Hide" : "Show") + " Optional Settings ", 1)
            ]),
            showOptionalSettings.value ? (openBlock(), createElementBlock("div", _hoisted_9$1, [
              _cache[12] || (_cache[12] = createBaseVNode("hr", { class: "section-divider" }, null, -1)),
              _cache[13] || (_cache[13] = createBaseVNode("div", { class: "table-sizes" }, "Table sizes", -1)),
              createBaseVNode("div", _hoisted_10, [
                createBaseVNode("div", _hoisted_11, [
                  _cache[8] || (_cache[8] = createBaseVNode("label", { for: "start-row" }, "Start Row", -1)),
                  withDirectives(createBaseVNode("input", {
                    id: "start-row",
                    "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => localExcelTable.value.start_row = $event),
                    type: "number",
                    class: "compact-input"
                  }, null, 512), [
                    [
                      vModelText,
                      localExcelTable.value.start_row,
                      void 0,
                      { number: true }
                    ]
                  ])
                ]),
                createBaseVNode("div", _hoisted_12, [
                  _cache[9] || (_cache[9] = createBaseVNode("label", { for: "end-row" }, "End Row", -1)),
                  withDirectives(createBaseVNode("input", {
                    id: "end-row",
                    "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => localExcelTable.value.end_row = $event),
                    type: "number",
                    class: "compact-input"
                  }, null, 512), [
                    [
                      vModelText,
                      localExcelTable.value.end_row,
                      void 0,
                      { number: true }
                    ]
                  ])
                ])
              ]),
              _cache[14] || (_cache[14] = createBaseVNode("hr", { class: "section-divider" }, null, -1)),
              createBaseVNode("div", _hoisted_13, [
                createBaseVNode("div", _hoisted_14, [
                  _cache[10] || (_cache[10] = createBaseVNode("label", { for: "start-column" }, "Start Column", -1)),
                  withDirectives(createBaseVNode("input", {
                    id: "start-column",
                    "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => localExcelTable.value.start_column = $event),
                    type: "number",
                    class: "compact-input"
                  }, null, 512), [
                    [
                      vModelText,
                      localExcelTable.value.start_column,
                      void 0,
                      { number: true }
                    ]
                  ])
                ]),
                createBaseVNode("div", _hoisted_15, [
                  _cache[11] || (_cache[11] = createBaseVNode("label", { for: "end-column" }, "End Column", -1)),
                  withDirectives(createBaseVNode("input", {
                    id: "end-column",
                    "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => localExcelTable.value.end_column = $event),
                    type: "number",
                    class: "compact-input"
                  }, null, 512), [
                    [
                      vModelText,
                      localExcelTable.value.end_column,
                      void 0,
                      { number: true }
                    ]
                  ])
                ])
              ])
            ])) : createCommentVNode("", true)
          ])) : createCommentVNode("", true)
        ])
      ])) : (openBlock(), createBlock(unref(CodeLoader), { key: 1 }));
    };
  }
});
const readExcel_vue_vue_type_style_index_0_scoped_e7395814_lang = "";
const ExcelTableConfig = /* @__PURE__ */ _export_sfc(_sfc_main$4, [["__scopeId", "data-v-e7395814"]]);
const _hoisted_1$2 = { class: "csv-table-settings" };
const _hoisted_2$1 = { class: "row" };
const _hoisted_3$1 = { class: "row" };
const _hoisted_4$1 = { class: "row" };
const _hoisted_5$1 = { class: "row" };
const _hoisted_6$1 = { class: "row" };
const _hoisted_7$1 = { class: "row" };
const _hoisted_8 = { class: "row" };
const _hoisted_9 = { class: "row" };
const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "readCsv",
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
    const updateParent = () => {
      emit("update:modelValue", localCsvTable.value);
    };
    const csv_settings = {
      delimiter_options: [",", ";", "|", "tab"],
      encoding_options: ["utf-8", "ISO-8859-1", "ASCII"],
      row_delimiter: ["\\n", "\\r\\n", "\\r"],
      quote_char: ['"', "'", "auto"]
    };
    watch(
      () => props.modelValue,
      (newVal) => {
        localCsvTable.value = newVal;
      },
      { deep: true }
    );
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1$2, [
        createBaseVNode("div", _hoisted_2$1, [
          _cache[8] || (_cache[8] = createBaseVNode("label", { for: "has-headers" }, "Has Headers:", -1)),
          createVNode(unref(ElCheckbox), {
            modelValue: localCsvTable.value.has_headers,
            "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => localCsvTable.value.has_headers = $event),
            size: "large",
            onChange: updateParent
          }, null, 8, ["modelValue"])
        ]),
        createBaseVNode("div", _hoisted_3$1, [
          _cache[9] || (_cache[9] = createBaseVNode("label", { for: "delimiter" }, "Delimiter:", -1)),
          createVNode(unref(ElSelect), {
            modelValue: localCsvTable.value.delimiter,
            "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => localCsvTable.value.delimiter = $event),
            placeholder: "Select delimiter",
            clearable: "",
            size: "small",
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
        createBaseVNode("div", _hoisted_4$1, [
          _cache[10] || (_cache[10] = createBaseVNode("label", { for: "encoding" }, "Encoding:", -1)),
          createVNode(unref(ElSelect), {
            modelValue: localCsvTable.value.encoding,
            "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => localCsvTable.value.encoding = $event),
            placeholder: "Select encoding",
            clearable: "",
            size: "small",
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
        ]),
        createBaseVNode("div", _hoisted_5$1, [
          _cache[11] || (_cache[11] = createBaseVNode("label", { for: "quote-char" }, "Quote Character:", -1)),
          createVNode(unref(ElSelect), {
            modelValue: localCsvTable.value.quote_char,
            "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => localCsvTable.value.quote_char = $event),
            placeholder: "Select quote character",
            clearable: "",
            size: "small",
            onChange: updateParent
          }, {
            default: withCtx(() => [
              (openBlock(true), createElementBlock(Fragment, null, renderList(csv_settings.quote_char, (option) => {
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
        createBaseVNode("div", _hoisted_6$1, [
          _cache[12] || (_cache[12] = createBaseVNode("label", { for: "row-delimiter" }, "New Line Delimiter:", -1)),
          createVNode(unref(ElSelect), {
            modelValue: localCsvTable.value.row_delimiter,
            "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => localCsvTable.value.row_delimiter = $event),
            placeholder: "Select new line delimiter",
            clearable: "",
            size: "small",
            onChange: updateParent
          }, {
            default: withCtx(() => [
              (openBlock(true), createElementBlock(Fragment, null, renderList(csv_settings.row_delimiter, (option) => {
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
        createBaseVNode("div", _hoisted_7$1, [
          _cache[13] || (_cache[13] = createBaseVNode("label", { for: "infer-schema-length" }, "Schema Infer Length:", -1)),
          createVNode(unref(ElSlider), {
            modelValue: localCsvTable.value.infer_schema_length,
            "onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => localCsvTable.value.infer_schema_length = $event),
            step: 1e3,
            max: 1e5,
            min: 0,
            "show-stops": "",
            size: "small",
            onChange: updateParent
          }, null, 8, ["modelValue"])
        ]),
        createBaseVNode("div", _hoisted_8, [
          _cache[14] || (_cache[14] = createBaseVNode("label", { for: "truncate-long-lines" }, "Truncate Long Lines:", -1)),
          createVNode(unref(ElCheckbox), {
            modelValue: localCsvTable.value.truncate_ragged_lines,
            "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => localCsvTable.value.truncate_ragged_lines = $event),
            size: "large",
            onChange: updateParent
          }, null, 8, ["modelValue"])
        ]),
        createBaseVNode("div", _hoisted_9, [
          _cache[15] || (_cache[15] = createBaseVNode("label", { for: "ignore-errors" }, "Ignore Errors:", -1)),
          createVNode(unref(ElCheckbox), {
            modelValue: localCsvTable.value.ignore_errors,
            "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => localCsvTable.value.ignore_errors = $event),
            size: "large",
            onChange: updateParent
          }, null, 8, ["modelValue"])
        ])
      ]);
    };
  }
});
const readCsv_vue_vue_type_style_index_0_scoped_d0b76f7b_lang = "";
const CsvTableConfig = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-d0b76f7b"]]);
const _hoisted_1$1 = { class: "parquet-table-settings" };
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "readParquet",
  props: {
    modelValue: {
      type: Object,
      required: true
    }
  },
  setup(__props) {
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1$1, _cache[0] || (_cache[0] = [
        createBaseVNode("div", { class: "message" }, [
          createBaseVNode("h2", null, "You are ready to flow!"),
          createBaseVNode("p", null, "Your Parquet table setup is complete. Enjoy the smooth data processing experience.")
        ], -1)
      ]));
    };
  }
});
const readParquet_vue_vue_type_style_index_0_scoped_0faf0508_lang = "";
const ParquetTableConfig = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-0faf0508"]]);
const _hoisted_1 = {
  key: 0,
  class: "listbox-wrapper"
};
const _hoisted_2 = { class: "listbox-wrapper" };
const _hoisted_3 = { class: "file-upload-container" };
const _hoisted_4 = {
  for: "file-upload",
  class: "file-upload-label"
};
const _hoisted_5 = { class: "file-label-text" };
const _hoisted_6 = { key: 0 };
const _hoisted_7 = { class: "listbox-wrapper" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "read",
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const selectedFile = ref(null);
    const isExcelFile = ref(false);
    const isCsvFile = ref(false);
    const isParquetFile = ref(false);
    const nodeRead = ref(null);
    const dataLoaded = ref(false);
    const selectedPath = ref("");
    const modalVisibleForOpen = ref(false);
    const getDisplayFileName = computed(() => {
      var _a, _b, _c;
      if ((_a = selectedFile.value) == null ? void 0 : _a.name) {
        return selectedFile.value.name;
      }
      if ((_c = (_b = nodeRead.value) == null ? void 0 : _b.received_file) == null ? void 0 : _c.name) {
        return nodeRead.value.received_file.name;
      }
      return "Choose a file...";
    });
    const receivedExcelTable = ref({
      name: "",
      path: "",
      file_type: "excel",
      sheet_name: "",
      start_row: 0,
      start_column: 0,
      end_row: 0,
      end_column: 0,
      has_headers: true,
      type_inference: false
    });
    const receivedCsvTable = ref({
      name: "",
      path: "",
      file_type: "csv",
      reference: "",
      starting_from_line: 0,
      delimiter: ",",
      has_headers: true,
      encoding: "utf-8",
      row_delimiter: "",
      quote_char: "",
      infer_schema_length: 1e3,
      truncate_ragged_lines: false,
      ignore_errors: false
    });
    const receivedParquetTable = ref({
      name: "",
      path: "",
      file_type: "parquet"
    });
    const handleFileChange = (fileInfo) => {
      var _a;
      try {
        if (!fileInfo) {
          console.warn("No file info provided");
          return;
        }
        const fileType = (_a = fileInfo.name.split(".").pop()) == null ? void 0 : _a.toLowerCase();
        if (!fileType) {
          console.warn("No file type detected");
          return;
        }
        isExcelFile.value = false;
        isCsvFile.value = false;
        isParquetFile.value = false;
        switch (fileType) {
          case "xlsx":
            isExcelFile.value = true;
            receivedExcelTable.value.path = fileInfo.path;
            receivedExcelTable.value.name = fileInfo.name;
            break;
          case "csv":
          case "txt":
            isCsvFile.value = true;
            receivedCsvTable.value.path = fileInfo.path;
            receivedCsvTable.value.name = fileInfo.name;
            break;
          case "parquet":
            isParquetFile.value = true;
            receivedParquetTable.value.path = fileInfo.path;
            receivedParquetTable.value.name = fileInfo.name;
            break;
          default:
            console.warn("Unsupported file type:", fileType);
            return;
        }
        selectedFile.value = fileInfo;
        selectedPath.value = fileInfo.path;
        modalVisibleForOpen.value = false;
      } catch (error) {
        console.error("Error handling file change:", error);
      }
    };
    const loadNodeData = async (nodeId) => {
      var _a;
      try {
        const nodeResult = await nodeStore.getNodeData(nodeId, false);
        if (!nodeResult) {
          console.warn("No node result received");
          dataLoaded.value = true;
          return;
        }
        nodeRead.value = nodeResult.setting_input;
        if (((_a = nodeResult.setting_input) == null ? void 0 : _a.is_setup) && nodeResult.setting_input.received_file) {
          const { file_type } = nodeResult.setting_input.received_file;
          isExcelFile.value = false;
          isCsvFile.value = false;
          isParquetFile.value = false;
          switch (file_type) {
            case "excel":
              isExcelFile.value = true;
              receivedExcelTable.value = nodeResult.setting_input.received_file;
              break;
            case "csv":
              isCsvFile.value = true;
              receivedCsvTable.value = nodeResult.setting_input.received_file;
              break;
            case "parquet":
              isParquetFile.value = true;
              receivedParquetTable.value = nodeResult.setting_input.received_file;
              break;
          }
          selectedPath.value = nodeResult.setting_input.received_file.path;
        }
        dataLoaded.value = true;
      } catch (error) {
        console.error("Error loading node data:", error);
        dataLoaded.value = true;
      }
    };
    const pushNodeData = async () => {
      try {
        dataLoaded.value = false;
        if (!nodeRead.value) {
          console.warn("No node read value available");
          dataLoaded.value = true;
          return;
        }
        nodeRead.value.is_setup = true;
        if (isExcelFile.value) {
          nodeRead.value.received_file = receivedExcelTable.value;
        } else if (isCsvFile.value) {
          nodeRead.value.received_file = receivedCsvTable.value;
        } else if (isParquetFile.value) {
          nodeRead.value.cache_results = false;
          nodeRead.value.received_file = receivedParquetTable.value;
        }
        await nodeStore.updateSettings(nodeRead);
      } catch (error) {
        console.error("Error pushing node data:", error);
      } finally {
        dataLoaded.value = true;
      }
    };
    __expose({
      loadNodeData,
      pushNodeData
    });
    return (_ctx, _cache) => {
      const _component_el_dialog = resolveComponent("el-dialog");
      return dataLoaded.value ? (openBlock(), createElementBlock("div", _hoisted_1, [
        createBaseVNode("div", _hoisted_2, [
          createBaseVNode("div", _hoisted_3, [
            createBaseVNode("div", {
              class: "file-upload-wrapper",
              onClick: _cache[0] || (_cache[0] = ($event) => modalVisibleForOpen.value = true)
            }, [
              createBaseVNode("label", _hoisted_4, [
                _cache[5] || (_cache[5] = createBaseVNode("i", { class: "fas fa-table file-icon" }, null, -1)),
                createBaseVNode("span", _hoisted_5, toDisplayString(getDisplayFileName.value), 1)
              ])
            ])
          ])
        ]),
        isCsvFile.value || isExcelFile.value || isParquetFile.value ? (openBlock(), createElementBlock("div", _hoisted_6, [
          createBaseVNode("div", _hoisted_7, [
            _cache[6] || (_cache[6] = createBaseVNode("div", { class: "listbox-subtitle" }, "File Specs", -1)),
            isExcelFile.value ? (openBlock(), createBlock(ExcelTableConfig, {
              key: 0,
              modelValue: receivedExcelTable.value,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => receivedExcelTable.value = $event)
            }, null, 8, ["modelValue"])) : createCommentVNode("", true),
            isCsvFile.value ? (openBlock(), createBlock(CsvTableConfig, {
              key: 1,
              modelValue: receivedCsvTable.value,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => receivedCsvTable.value = $event)
            }, null, 8, ["modelValue"])) : createCommentVNode("", true),
            isParquetFile.value ? (openBlock(), createBlock(ParquetTableConfig, {
              key: 2,
              modelValue: receivedParquetTable.value,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => receivedParquetTable.value = $event)
            }, null, 8, ["modelValue"])) : createCommentVNode("", true)
          ])
        ])) : createCommentVNode("", true),
        createVNode(_component_el_dialog, {
          modelValue: modalVisibleForOpen.value,
          "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => modalVisibleForOpen.value = $event),
          title: "Select a file to Read",
          width: "70%"
        }, {
          default: withCtx(() => [
            createVNode(FileBrowser, {
              "allowed-file-types": ["csv", "txt", "parquet", "xlsx"],
              mode: "open",
              onFileSelected: handleFileChange
            })
          ]),
          _: 1
        }, 8, ["modelValue"])
      ])) : (openBlock(), createBlock(unref(CodeLoader), { key: 1 }));
    };
  }
});
const read_vue_vue_type_style_index_0_scoped_221ad292_lang = "";
const readInput = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-221ad292"]]);
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Read",
  props: {
    nodeId: {
      type: Number,
      required: true
    }
  },
  setup(__props) {
    const props = __props;
    const nodeStore = useNodeStore();
    const childComp = ref(null);
    const closeOnDrawer = () => {
      var _a;
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
      return openBlock(), createElementBlock("div", null, [
        createVNode(NodeButton, {
          ref: "nodeButton",
          "node-id": __props.nodeId,
          "image-src": "input_data.png",
          title: `${__props.nodeId}: Read data`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Read data",
            intro: "Read data from a file"
          }),
          createVNode(readInput, {
            ref_key: "childComp",
            ref: childComp,
            "node-id": __props.nodeId
          }, null, 8, ["node-id"])
        ])) : createCommentVNode("", true)
      ]);
    };
  }
});
export {
  _sfc_main as default
};
