<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-diagram-3 me-2"></i>BOM 관리</h5>
        <p class="text-muted small mb-0">제품 레시피(BOM)를 등록하고 기존 BOM을 조회·수정합니다</p>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">전체 BOM</div>
          <div class="fw-bold" style="font-size:1.6rem">{{ kpi.total }}<span class="small fw-normal text-muted ms-1">건</span></div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">활성 BOM</div>
          <div class="fw-bold text-success" style="font-size:1.6rem">{{ kpi.active }}<span class="small fw-normal text-muted ms-1">건</span></div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">알레르겐 포함</div>
          <div class="fw-bold text-warning" style="font-size:1.6rem">{{ kpi.allergen }}<span class="small fw-normal text-muted ms-1">건</span></div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card erp-card p-3">
          <div class="text-muted small mb-1">검토중</div>
          <div class="fw-bold text-info" style="font-size:1.6rem">{{ kpi.review }}<span class="small fw-normal text-muted ms-1">건</span></div>
        </div>
      </div>
    </div>

    <!-- 토글 -->
    <div class="d-flex gap-3 mb-3 view-tabs">
      <div class="tab-item" :class="{ active: activeTab === 'register' }" @click="activeTab = 'register'">BOM 등록</div>
      <div class="tab-item" :class="{ active: activeTab === 'manage' }" @click="activeTab = 'manage'">BOM 관리</div>
    </div>

    <!-- ===================== BOM 등록 ===================== -->
    <div v-if="activeTab === 'register'" class="card erp-card">
      <div class="card-body">
        <div class="row g-2 mb-3">
          <div class="col-md-6">
            <label class="form-label small fw-semibold">제품명 <span class="text-danger">*</span></label>
            <input v-model="form.productname" type="text" class="form-control form-control-sm" placeholder="예: 망고코코넛 음료 500ml" />
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-semibold">BOM코드</label>
            <input v-model="form.bomcode" type="text" class="form-control form-control-sm" />
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-semibold">유형</label>
            <select v-model="form.bomtype" class="form-select form-select-sm">
              <option value="완제품">완제품</option>
              <option value="반제품">반제품</option>
            </select>
          </div>
        </div>
        <div class="row g-2 mb-3">
          <div class="col-md-3">
            <label class="form-label small fw-semibold">기준 배치 수량</label>
            <input v-model.number="form.basisquantity" type="number" min="0" class="form-control form-control-sm" />
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-semibold">기준 단위</label>
            <input v-model="form.basisunit" type="text" class="form-control form-control-sm" placeholder="예: L, kg, EA" />
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-semibold">리비전</label>
            <input v-model="form.revision" type="text" class="form-control form-control-sm" placeholder="예: R01" />
          </div>
          <div class="col-md-3">
            <label class="form-label small fw-semibold">상태</label>
            <select v-model="form.status" class="form-select form-select-sm">
              <option value="활성">활성</option>
              <option value="검토중">검토중</option>
              <option value="폐기">폐기</option>
            </select>
          </div>
        </div>
        <div class="mb-3">
          <label class="form-label small fw-semibold">알레르겐</label>
          <input v-model="form.allergen" type="text" class="form-control form-control-sm" placeholder="예: 우유, 대두 (없으면 비워두세요)" />
        </div>

        <hr />
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span class="fw-semibold small">구성 품목</span>
          <span class="small text-muted">배치원가 합계: {{ fmtCurrency(draftBatchCost) }}</span>
        </div>
        <table class="table table-sm mb-2 align-middle">
          <thead class="table-light">
            <tr><th>자재</th><th class="text-end">수량</th><th class="text-end">배합비</th><th class="text-end">원가</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in draftComponents" :key="idx">
              <td class="small">{{ materialName(row.materialid) }}</td>
              <td class="small text-end">{{ row.quantity }}</td>
              <td class="small text-end">{{ row.ratio }}</td>
              <td class="small text-end">{{ fmtCurrency(componentLineCost(row)) }}</td>
              <td><button class="btn-icon text-danger" @click="draftComponents.splice(idx,1)"><i class="bi bi-trash"></i></button></td>
            </tr>
            <tr v-if="draftComponents.length === 0">
              <td colspan="5" class="text-center text-muted small py-3">추가된 구성 품목이 없습니다</td>
            </tr>
          </tbody>
        </table>
        <div class="d-flex gap-2 align-items-end mb-3">
          <div style="width:220px">
            <select v-model="newComponent.materialid" class="form-select form-select-sm">
              <option value="">자재 선택</option>
              <option v-for="m in procurementStore.materials" :key="m.materialid" :value="m.materialid">{{ m.materialname }}</option>
            </select>
          </div>
          <div style="width:110px">
            <input v-model.number="newComponent.quantity" type="number" min="0" class="form-control form-control-sm" placeholder="수량" />
          </div>
          <div style="width:110px">
            <input v-model.number="newComponent.ratio" type="number" min="0" step="0.01" class="form-control form-control-sm" placeholder="배합비" />
          </div>
          <button class="btn btn-sm btn-outline-secondary" @click="addDraftComponent"><i class="bi bi-plus-lg me-1"></i>품목 추가</button>
        </div>

        <div v-if="registerError" class="alert alert-danger small py-2">{{ registerError }}</div>
        <button class="btn btn-primary btn-sm" :disabled="registerSaving" @click="submitRegister">
          <span v-if="registerSaving" class="spinner-border spinner-border-sm me-1"></span>BOM 등록
        </button>
      </div>
    </div>

    <!-- ===================== BOM 관리 ===================== -->
    <div v-else>
      <div class="card erp-card mb-3">
        <div class="card-body py-3">
          <div class="row g-2 align-items-end">
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">유형</label>
              <select v-model="filter.bomtype" class="form-select form-select-sm">
                <option value="">전체</option>
                <option value="완제품">완제품</option>
                <option value="반제품">반제품</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">상태</label>
              <select v-model="filter.status" class="form-select form-select-sm">
                <option value="">전체</option>
                <option value="활성">활성</option>
                <option value="검토중">검토중</option>
                <option value="폐기">폐기</option>
              </select>
            </div>
            <div class="col-md-3 d-flex gap-2">
              <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="filter.bomtype=''; filter.status=''">
                <i class="bi bi-arrow-counterclockwise me-1"></i>초기화
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="card erp-card mb-3">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>BOM코드</th><th>제품명</th><th>유형</th><th class="text-end">기준 배치</th>
                  <th class="text-end">배치원가</th><th>알레르겐</th><th>상태</th><th>관리</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="b in filteredBoms" :key="b.bomid" class="cursor-pointer" :class="{ 'table-active': selectedBomId === b.bomid }" @click="selectBom(b.bomid)">
                  <td class="small text-muted">{{ b.bomcode }}</td>
                  <td class="small fw-semibold">{{ b.productname }}</td>
                  <td class="small">{{ b.bomtype }}</td>
                  <td class="small text-end">{{ b.basisquantity }} {{ b.basisunit }}</td>
                  <td class="small text-end">{{ fmtCurrency(b.batchcost) }}</td>
                  <td class="small text-muted">{{ b.allergen || '-' }}</td>
                  <td><span class="badge" :class="bomStatusMeta(b.status).cls">{{ b.status }}</span></td>
                  <td>
                    <button class="btn-icon text-danger" title="삭제" @click.stop="deleteBom(b)"><i class="bi bi-trash"></i></button>
                  </td>
                </tr>
                <tr v-if="filteredBoms.length === 0">
                  <td colspan="8" class="text-center text-muted small py-4">조건에 맞는 BOM이 없습니다</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 선택된 BOM 상세 -->
      <div v-if="selectedBom" class="card erp-card">
        <div class="card-header bg-white py-2 d-flex justify-content-between align-items-center">
          <span class="fw-semibold small">{{ selectedBom.productname }} ({{ selectedBom.bomcode }})</span>
          <div class="d-flex gap-2 align-items-end">
            <select v-model="editForm.status" class="form-select form-select-sm" style="width:120px">
              <option value="활성">활성</option>
              <option value="검토중">검토중</option>
              <option value="폐기">폐기</option>
            </select>
            <input v-model="editForm.revision" type="text" class="form-control form-control-sm" style="width:100px" placeholder="리비전" />
            <button class="btn btn-sm btn-primary" @click="saveBomHeader">저장</button>
          </div>
        </div>
        <div class="card-body p-0">
          <table class="table table-sm mb-0 align-middle">
            <thead class="table-light">
              <tr><th>코드</th><th>품목명</th><th class="text-end">수량</th><th class="text-end">배합비</th><th>알레르겐</th><th class="text-end">원가</th><th></th></tr>
            </thead>
            <tbody>
              <tr v-for="c in selectedBom.components" :key="c.id">
                <td class="small text-muted">{{ c.materialid }}</td>
                <td class="small">{{ c.material_name }}</td>
                <td class="small text-end" style="width:90px">
                  <input v-model.number="compEdits[c.id]" type="number" class="form-control form-control-sm text-end" @change="saveComponent(c)" />
                </td>
                <td class="small text-end">{{ c.ratio ?? '-' }}</td>
                <td class="small text-muted">{{ materialAllergen(c.materialid) || '-' }}</td>
                <td class="small text-end">{{ fmtCurrency(c.linecost) }}</td>
                <td><button class="btn-icon text-danger" @click="deleteComponent(c)"><i class="bi bi-trash"></i></button></td>
              </tr>
              <tr v-if="selectedBom.components.length === 0">
                <td colspan="7" class="text-center text-muted small py-3">구성 품목이 없습니다</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="card-footer bg-white py-2">
          <div class="d-flex gap-2 align-items-end">
            <select v-model="addComponentForm.materialid" class="form-select form-select-sm" style="max-width:220px">
              <option value="">자재 추가 선택</option>
              <option v-for="m in procurementStore.materials" :key="m.materialid" :value="m.materialid">{{ m.materialname }}</option>
            </select>
            <input v-model.number="addComponentForm.quantity" type="number" min="0" class="form-control form-control-sm" style="width:110px" placeholder="수량" />
            <input v-model.number="addComponentForm.ratio" type="number" min="0" step="0.01" class="form-control form-control-sm" style="width:110px" placeholder="배합비" />
            <button class="btn btn-sm btn-outline-secondary" @click="addComponentToSelected"><i class="bi bi-plus-lg me-1"></i>품목 추가</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useProcurementStore } from '@/stores/procurement'
import { procurementApi } from '@/api/procurement'

const procurementStore = useProcurementStore()

const activeTab = ref('register')

const kpi = computed(() => {
  const list = procurementStore.boms
  return {
    total: list.length,
    active: list.filter((b) => b.status === '활성').length,
    allergen: list.filter((b) => b.allergen).length,
    review: list.filter((b) => b.status === '검토중').length,
  }
})

function fmtCurrency(v) {
  if (v == null) return '-'
  return '₩' + Math.round(Number(v)).toLocaleString('ko-KR')
}
function bomStatusMeta(status) {
  const map = {
    '활성': { cls: 'bg-success-subtle text-success border border-success-subtle' },
    '검토중': { cls: 'bg-info-subtle text-info border border-info-subtle' },
    '폐기': { cls: 'bg-secondary-subtle text-secondary border border-secondary-subtle' },
  }
  return map[status] || { cls: 'bg-secondary-subtle text-secondary' }
}
function materialName(id) {
  return procurementStore.materials.find((m) => m.materialid === id)?.materialname || id
}
function materialAllergen(id) {
  return procurementStore.materials.find((m) => m.materialid === id)?.allergen
}

// ===================== BOM 등록 =====================
function nextBomCode() {
  let max = 0
  procurementStore.boms.forEach((b) => {
    const m = /BOM-FW-(\d+)/.exec(b.bomcode)
    if (m) max = Math.max(max, parseInt(m[1], 10))
  })
  return `BOM-FW-${String(max + 1).padStart(3, '0')}`
}

const form = reactive({
  productname: '', bomcode: '', bomtype: '완제품', basisquantity: 0, basisunit: 'kg',
  revision: 'R01', status: '활성', allergen: '',
})
watch(() => procurementStore.boms.length, () => { if (!form.bomcode) form.bomcode = nextBomCode() })

const draftComponents = ref([])
const newComponent = reactive({ materialid: '', quantity: 0, ratio: 0 })

function componentLineCost(row) {
  const material = procurementStore.materials.find((m) => m.materialid === row.materialid)
  return (Number(material?.unitcost) || 0) * (Number(row.quantity) || 0)
}
const draftBatchCost = computed(() => draftComponents.value.reduce((s, r) => s + componentLineCost(r), 0))

function addDraftComponent() {
  if (!newComponent.materialid || !newComponent.quantity) return
  draftComponents.value.push({ ...newComponent })
  newComponent.materialid = ''
  newComponent.quantity = 0
  newComponent.ratio = 0
}

const registerSaving = ref(false)
const registerError = ref('')

async function submitRegister() {
  if (!form.productname || !form.bomcode) {
    registerError.value = '제품명과 BOM코드를 입력하세요.'
    return
  }
  registerSaving.value = true
  registerError.value = ''
  try {
    const res = await procurementApi.createBom({
      bomcode: form.bomcode,
      productname: form.productname,
      bomtype: form.bomtype,
      basisquantity: form.basisquantity,
      basisunit: form.basisunit,
      revision: form.revision,
      status: form.status,
      allergen: form.allergen || null,
      batchcost: draftBatchCost.value,
    })
    const newBomId = res.data.bomid
    for (const row of draftComponents.value) {
      await procurementApi.createBomComponent({
        bomid: newBomId,
        materialid: row.materialid,
        quantity: row.quantity,
        ratio: row.ratio || null,
        linecost: componentLineCost(row),
      })
    }
    form.productname = ''
    form.bomcode = ''
    form.allergen = ''
    draftComponents.value = []
    await procurementStore.fetchBoms()
    form.bomcode = nextBomCode()
    activeTab.value = 'manage'
  } catch (e) {
    registerError.value = e?.response?.data ? JSON.stringify(e.response.data) : 'BOM 등록에 실패했습니다.'
  } finally {
    registerSaving.value = false
  }
}

// ===================== BOM 관리 =====================
const filter = reactive({ bomtype: '', status: '' })
const filteredBoms = computed(() => {
  let list = procurementStore.boms
  if (filter.bomtype) list = list.filter((b) => b.bomtype === filter.bomtype)
  if (filter.status) list = list.filter((b) => b.status === filter.status)
  return list
})

const selectedBomId = ref(null)
const selectedBom = computed(() => procurementStore.boms.find((b) => b.bomid === selectedBomId.value) || null)
const compEdits = reactive({})
const editForm = reactive({ status: '활성', revision: '' })

function selectBom(id) {
  selectedBomId.value = selectedBomId.value === id ? null : id
  if (selectedBom.value) {
    editForm.status = selectedBom.value.status
    editForm.revision = selectedBom.value.revision
  }
}

watch(selectedBom, (bom) => {
  if (!bom) return
  bom.components.forEach((c) => {
    if (compEdits[c.id] === undefined) compEdits[c.id] = c.quantity
  })
}, { immediate: true, deep: true })

async function saveBomHeader() {
  if (!selectedBom.value) return
  try {
    await procurementApi.updateBom(selectedBom.value.bomid, { ...selectedBom.value, status: editForm.status, revision: editForm.revision })
    await procurementStore.fetchBoms()
  } catch {
    alert('저장에 실패했습니다.')
  }
}

async function saveComponent(c) {
  const material = procurementStore.materials.find((m) => m.materialid === c.materialid)
  const quantity = compEdits[c.id]
  const linecost = (Number(material?.unitcost) || 0) * (Number(quantity) || 0)
  try {
    await procurementApi.updateBomComponent(c.id, { ...c, quantity, linecost })
    await procurementStore.fetchBoms()
  } catch {
    alert('저장에 실패했습니다.')
  }
}

async function deleteComponent(c) {
  if (!confirm('이 구성 품목을 삭제하시겠습니까?')) return
  try {
    await procurementApi.deleteBomComponent(c.id)
    await procurementStore.fetchBoms()
  } catch {
    alert('삭제에 실패했습니다.')
  }
}

const addComponentForm = reactive({ materialid: '', quantity: 0, ratio: 0 })
async function addComponentToSelected() {
  if (!selectedBom.value || !addComponentForm.materialid || !addComponentForm.quantity) return
  const material = procurementStore.materials.find((m) => m.materialid === addComponentForm.materialid)
  try {
    await procurementApi.createBomComponent({
      bomid: selectedBom.value.bomid,
      materialid: addComponentForm.materialid,
      quantity: addComponentForm.quantity,
      ratio: addComponentForm.ratio || null,
      linecost: (Number(material?.unitcost) || 0) * addComponentForm.quantity,
    })
    addComponentForm.materialid = ''
    addComponentForm.quantity = 0
    addComponentForm.ratio = 0
    await procurementStore.fetchBoms()
  } catch {
    alert('품목 추가에 실패했습니다.')
  }
}

async function deleteBom(b) {
  if (!confirm(`${b.bomcode} (${b.productname})을 삭제하시겠습니까?`)) return
  try {
    await procurementApi.deleteBom(b.bomid)
    if (selectedBomId.value === b.bomid) selectedBomId.value = null
    await procurementStore.fetchBoms()
  } catch {
    alert('삭제에 실패했습니다. 이 BOM을 참조하는 구성 품목이 있는지 확인하세요.')
  }
}

onMounted(async () => {
  await procurementStore.fetchAll()
  form.bomcode = nextBomCode()
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-header { border-bottom: 1px solid #f1f5f9; border-radius: 12px 12px 0 0; }
.erp-card .card-footer { border-top: 1px solid #f1f5f9; border-radius: 0 0 12px 12px; }
.view-tabs { border-bottom: 1px solid #e5e7eb; }
.tab-item {
  padding: 8px 4px 10px; font-weight: 600; font-size: 0.92rem; color: #94a3b8;
  cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px;
}
.tab-item.active { color: #2563eb; border-bottom-color: #2563eb; }
.tab-item:hover { color: #2563eb; }
.cursor-pointer { cursor: pointer; }
.btn-icon { border: none; background: transparent; color: #64748b; padding: 2px 6px; border-radius: 6px; cursor: pointer; }
.btn-icon:hover { background: #f1f5f9; color: #1e293b; }
</style>
