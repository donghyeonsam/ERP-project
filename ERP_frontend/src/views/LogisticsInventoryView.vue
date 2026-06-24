<template>
  <div>
    <div class="d-flex align-items-start justify-content-between mb-4">
      <div>
        <h5 class="fw-bold mb-1"><i class="bi bi-boxes me-2"></i>재고관리</h5>
        <p class="text-muted small mb-0">{{ subtitle }}</p>
      </div>
    </div>

    <!-- 메인 토글 -->
    <div class="d-flex gap-2 mb-4">
      <button class="btn btn-sm" :class="activeMain === 'status' ? 'btn-primary' : 'btn-outline-secondary'" @click="activeMain = 'status'">재고현황</button>
      <button class="btn btn-sm" :class="activeMain === 'count' ? 'btn-primary' : 'btn-outline-secondary'" @click="activeMain = 'count'">재고실사</button>
      <button class="btn btn-sm" :class="activeMain === 'expiry' ? 'btn-primary' : 'btn-outline-secondary'" @click="activeMain = 'expiry'">유통기한관리</button>
    </div>

    <!-- ===================== 1. 재고현황 ===================== -->
    <div v-if="activeMain === 'status'">
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">총 현재고</div>
            <div class="fw-bold" style="font-size:1.4rem">{{ statusKpi.totalStock.toLocaleString() }}<span class="small fw-normal text-muted ms-1">개</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">가용재고</div>
            <div class="fw-bold" style="font-size:1.4rem">{{ statusKpi.available.toLocaleString() }}<span class="small fw-normal text-muted ms-1">개</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">적치율 초과 창고</div>
            <div class="fw-bold text-danger" style="font-size:1.4rem">{{ statusKpi.overCapacity }}<span class="small fw-normal text-muted ms-1">개</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">안전재고 미달 품목</div>
            <div class="fw-bold text-warning" style="font-size:1.4rem">{{ statusKpi.belowSafety }}<span class="small fw-normal text-muted ms-1">종</span></div>
          </div>
        </div>
      </div>

      <div class="card erp-card mb-3">
        <div class="card-body py-3">
          <div class="row g-2 align-items-end">
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">창고</label>
              <select v-model="statusFilter.warehouse" class="form-select form-select-sm">
                <option value="">전체</option>
                <option v-for="w in warehouseList" :key="w" :value="w">{{ w }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">구분</label>
              <select v-model="statusFilter.category" class="form-select form-select-sm">
                <option value="">전체</option>
                <option value="상온">상온</option>
                <option value="냉장">냉장</option>
                <option value="냉동">냉동</option>
              </select>
            </div>
            <div class="col-md-3 d-flex gap-2">
              <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="statusFilter.warehouse=''; statusFilter.category=''">
                <i class="bi bi-arrow-counterclockwise me-1"></i>초기화
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="card erp-card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>창고명</th><th>구분</th><th class="text-end">총 용량</th>
                  <th class="text-end">현재고</th><th class="text-end">가용재고</th>
                  <th class="text-end">출고예정</th><th>적치율</th><th>상태</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in filteredWarehouseRows" :key="row.warehouse">
                  <td class="small fw-semibold">{{ row.warehouse }}</td>
                  <td class="small text-muted">{{ row.category }}</td>
                  <td class="small text-end">{{ row.capacity.toLocaleString() }}</td>
                  <td class="small text-end">{{ row.stock.toLocaleString() }}</td>
                  <td class="small text-end">{{ row.available.toLocaleString() }}</td>
                  <td class="small text-end">{{ row.outbound.toLocaleString() }}</td>
                  <td style="min-width:120px">
                    <div class="d-flex align-items-center gap-2">
                      <div class="progress flex-grow-1" style="height:6px">
                        <div class="progress-bar" :class="rateBarClass(row.rate)" :style="{ width: Math.min(row.rate,100) + '%' }"></div>
                      </div>
                      <span class="small text-muted">{{ row.rate.toFixed(0) }}%</span>
                    </div>
                  </td>
                  <td><span class="badge" :class="statusMeta(rateStatus(row.rate)).cls">{{ rateStatus(row.rate) }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================== 2. 재고실사 ===================== -->
    <div v-else-if="activeMain === 'count'">
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">금월 실사 건수</div>
            <div class="fw-bold" style="font-size:1.4rem">{{ countKpi.monthly }}<span class="small fw-normal text-muted ms-1">건</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">완료율</div>
            <div class="fw-bold" style="font-size:1.4rem">{{ countKpi.completionRate.toFixed(0) }}<span class="small fw-normal text-muted ms-1">%</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">일치율</div>
            <div class="fw-bold text-success" style="font-size:1.4rem">{{ countKpi.matchRate.toFixed(1) }}<span class="small fw-normal text-muted ms-1">%</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">차이 발생 건</div>
            <div class="fw-bold text-danger" style="font-size:1.4rem">{{ countKpi.diffCount }}<span class="small fw-normal text-muted ms-1">건</span></div>
          </div>
        </div>
      </div>

      <div class="d-flex gap-3 mb-3 view-tabs">
        <div class="tab-item" :class="{ active: countTab === 'plan' }" @click="countTab = 'plan'">실사계획</div>
        <div class="tab-item" :class="{ active: countTab === 'register' }" @click="countTab = 'register'">실사등록</div>
        <div class="tab-item" :class="{ active: countTab === 'adjust' }" @click="countTab = 'adjust'">차이조정</div>
      </div>

      <!-- 실사계획 -->
      <div v-if="countTab === 'plan'">
        <div class="card erp-card mb-3">
          <div class="card-body py-3">
            <div class="row g-2 align-items-end">
              <div class="col-md-3">
                <label class="form-label small text-muted mb-1">실사유형</label>
                <select v-model="planFilter.type" class="form-select form-select-sm">
                  <option value="">전체</option>
                  <option value="정기">정기</option>
                  <option value="특별">특별</option>
                  <option value="수시">수시</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label small text-muted mb-1">상태</label>
                <select v-model="planFilter.status" class="form-select form-select-sm">
                  <option value="">전체</option>
                  <option value="대기">대기</option>
                  <option value="진행중">진행중</option>
                  <option value="완료">완료</option>
                </select>
              </div>
              <div class="col-md-3 d-flex gap-2">
                <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="planFilter.type=''; planFilter.status=''">
                  <i class="bi bi-arrow-counterclockwise me-1"></i>초기화
                </button>
              </div>
              <div class="col-md-3 d-flex justify-content-end">
                <button class="btn btn-sm btn-primary" @click="openPlanModal"><i class="bi bi-plus-lg me-1"></i>실사계획 등록</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="inventoryStore.loading" class="text-center py-5"><span class="spinner-border"></span></div>
        <div v-else class="card erp-card">
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-sm table-hover mb-0 align-middle">
                <thead class="table-light">
                  <tr>
                    <th>계획번호</th><th>유형</th><th>범위</th><th>대상창고</th>
                    <th>예정일</th><th>담당자</th><th>진행률</th><th>상태</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in filteredPlans" :key="p.id">
                    <td class="small text-muted">{{ p.code }}</td>
                    <td class="small">{{ p.count_type }}</td>
                    <td class="small">{{ p.scope || '-' }}</td>
                    <td class="small">{{ p.warehouse }}</td>
                    <td class="small text-muted">{{ p.scheduled_date }}</td>
                    <td class="small">{{ p.manager_name || '-' }}</td>
                    <td class="small">{{ p.progress_rate }}%</td>
                    <td><span class="badge" :class="planStatusMeta(p.status).cls">{{ p.status }}</span></td>
                  </tr>
                  <tr v-if="filteredPlans.length === 0">
                    <td colspan="8" class="text-center text-muted small py-4">실사 계획이 없습니다</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- 실사등록 -->
      <div v-else-if="countTab === 'register'">
        <div class="card erp-card mb-3">
          <div class="card-body py-3">
            <label class="form-label small text-muted mb-1">실사계획 선택</label>
            <select v-model="registerPlanId" class="form-select form-select-sm" style="max-width:420px">
              <option value="">선택</option>
              <option v-for="p in inventoryStore.countPlans" :key="p.id" :value="p.id">
                {{ p.code }} · {{ p.scope }} ({{ p.status }})
              </option>
            </select>
          </div>
        </div>

        <div v-if="selectedPlan" class="card erp-card mb-3">
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-sm mb-0 align-middle">
                <thead class="table-light">
                  <tr><th>품목</th><th class="text-end">전산재고</th><th class="text-end">실사수량</th><th class="text-end">차이</th><th></th></tr>
                </thead>
                <tbody>
                  <tr v-for="item in selectedPlan.items" :key="item.id">
                    <td class="small">{{ item.product_name }}</td>
                    <td class="small text-end">{{ item.system_qty }}</td>
                    <td class="small text-end" style="width:120px">
                      <input v-model.number="itemEdits[item.id]" type="number" class="form-control form-control-sm text-end" />
                    </td>
                    <td class="small text-end" :class="diffClass(itemEdits[item.id], item.system_qty)">
                      {{ itemEdits[item.id] != null ? (itemEdits[item.id] - item.system_qty) : '-' }}
                    </td>
                    <td><button class="btn btn-sm btn-outline-primary" @click="saveCountItem(item)">저장</button></td>
                  </tr>
                  <tr v-if="selectedPlan.items.length === 0">
                    <td colspan="5" class="text-center text-muted small py-4">등록된 품목이 없습니다</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="card-footer bg-white py-2">
            <div class="d-flex gap-2 align-items-end">
              <select v-model="newItemProductId" class="form-select form-select-sm" style="max-width:260px">
                <option value="">품목 추가 선택</option>
                <option v-for="pr in ssafyStore.products" :key="pr.productid" :value="pr.productid">{{ pr.productname }}</option>
              </select>
              <button class="btn btn-sm btn-outline-secondary" @click="addCountItem"><i class="bi bi-plus-lg me-1"></i>품목 추가</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 차이조정 -->
      <div v-else class="card erp-card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm mb-0 align-middle">
              <thead class="table-light">
                <tr><th>계획번호</th><th>품목</th><th class="text-end">전산재고</th><th class="text-end">실사수량</th><th class="text-end">차이</th><th>비고</th></tr>
              </thead>
              <tbody>
                <tr v-for="row in diffRows" :key="row.id">
                  <td class="small text-muted">{{ row.planCode }}</td>
                  <td class="small">{{ row.product_name }}</td>
                  <td class="small text-end">{{ row.system_qty }}</td>
                  <td class="small text-end">{{ row.counted_qty }}</td>
                  <td class="small text-end" :class="row.diff > 0 ? 'text-success' : 'text-danger'">{{ row.diff > 0 ? '+' : '' }}{{ row.diff }}</td>
                  <td class="small text-muted">{{ row.note || '-' }}</td>
                </tr>
                <tr v-if="diffRows.length === 0">
                  <td colspan="6" class="text-center text-muted small py-4">차이가 발생한 품목이 없습니다</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================== 3. 유통기한관리 ===================== -->
    <div v-else>
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">기한경과</div>
            <div class="fw-bold text-danger" style="font-size:1.4rem">{{ expiryKpi.expired }}<span class="small fw-normal text-muted ms-1">건</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">D-7 이내 임박</div>
            <div class="fw-bold text-danger" style="font-size:1.4rem">{{ expiryKpi.critical }}<span class="small fw-normal text-muted ms-1">건</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">D-30 이내</div>
            <div class="fw-bold text-warning" style="font-size:1.4rem">{{ expiryKpi.warning }}<span class="small fw-normal text-muted ms-1">건</span></div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card erp-card p-3">
            <div class="text-muted small mb-1">정상 관리 중</div>
            <div class="fw-bold text-success" style="font-size:1.4rem">{{ expiryKpi.normal }}<span class="small fw-normal text-muted ms-1">건</span></div>
          </div>
        </div>
      </div>

      <div class="d-flex gap-3 mb-3 view-tabs">
        <div class="tab-item" :class="{ active: expiryTab === 'all' }" @click="expiryTab = 'all'">전체</div>
        <div class="tab-item" :class="{ active: expiryTab === 'd30' }" @click="expiryTab = 'd30'">D-30 이내</div>
        <div class="tab-item" :class="{ active: expiryTab === 'expired' }" @click="expiryTab = 'expired'">기한경과</div>
        <div class="tab-item" :class="{ active: expiryTab === 'fifo' }" @click="expiryTab = 'fifo'">FIFO 관리</div>
      </div>

      <div class="card erp-card mb-3">
        <div class="card-body py-3">
          <div class="row g-2 align-items-end">
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">품목군</label>
              <select v-model="expiryFilter.category" class="form-select form-select-sm">
                <option value="">전체</option>
                <option v-for="c in ssafyStore.categories" :key="c.categoryid" :value="c.categoryname">{{ c.categoryname }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">창고</label>
              <select v-model="expiryFilter.warehouse" class="form-select form-select-sm">
                <option value="">전체</option>
                <option v-for="w in warehouseList" :key="w" :value="w">{{ w }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label small text-muted mb-1">품목명</label>
              <input v-model="expiryFilter.name" type="text" class="form-control form-control-sm" placeholder="품목명 검색" />
            </div>
            <div class="col-md-3 d-flex gap-2">
              <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="resetExpiryFilter">
                <i class="bi bi-arrow-counterclockwise me-1"></i>초기화
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="card erp-card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>품목코드</th><th>품목명</th><th>Lot번호</th><th>창고</th>
                  <th>제조일</th><th>유통기한</th><th class="text-end">잔여일</th>
                  <th class="text-end">수량</th><th>상태</th><th>관리</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="lot in pagedLots" :key="lot.id">
                  <td class="small text-muted">P-{{ lot.productid }}</td>
                  <td class="small fw-semibold">{{ lot.productName }}</td>
                  <td class="small text-muted">{{ lot.lotNumber }}</td>
                  <td class="small">{{ lot.warehouse }}</td>
                  <td class="small text-muted">{{ lot.manufactureDate }}</td>
                  <td class="small text-muted">{{ lot.expiryDate }}</td>
                  <td class="small text-end" :class="lot.remainingDays < 0 ? 'text-danger fw-semibold' : ''">
                    {{ lot.remainingDays >= 0 ? `D-${lot.remainingDays}` : `D+${-lot.remainingDays}` }}
                  </td>
                  <td class="small text-end">{{ lot.quantity.toLocaleString() }}</td>
                  <td><span class="badge" :class="expiryStatusMeta(lot.status).cls">{{ expiryStatusMeta(lot.status).label }}</span></td>
                  <td><button class="btn btn-sm btn-outline-secondary" @click="processLot(lot)">처리</button></td>
                </tr>
                <tr v-if="pagedLots.length === 0">
                  <td colspan="10" class="text-center text-muted small py-4">조건에 맞는 항목이 없습니다</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card-footer d-flex justify-content-between align-items-center py-2 bg-white">
          <span class="small text-muted">총 {{ sortedLots.length.toLocaleString() }}건 중 {{ lotPageStart + 1 }}-{{ lotPageEnd }}</span>
          <div class="d-flex gap-1 align-items-center">
            <button class="btn btn-sm btn-outline-secondary" :disabled="lotPage === 1" @click="lotPage--"><i class="bi bi-chevron-left"></i></button>
            <span class="small mx-2">{{ lotPage }} / {{ lotTotalPages }}</span>
            <button class="btn btn-sm btn-outline-secondary" :disabled="lotPage === lotTotalPages" @click="lotPage++"><i class="bi bi-chevron-right"></i></button>
          </div>
        </div>
      </div>
    </div>

    <!-- 실사계획 등록 모달 -->
    <Teleport to="body">
      <div v-if="showPlanModal" class="modal-backdrop-custom" @click.self="showPlanModal = false">
        <div class="modal-panel shadow-lg" style="width:440px">
          <div class="modal-panel-header">
            <span class="fw-bold small"><i class="bi bi-clipboard-check me-2 text-primary"></i>실사계획 등록</span>
            <button class="btn-close-panel" @click="showPlanModal = false"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-panel-body">
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">실사유형</label>
                <select v-model="planForm.count_type" class="form-select form-select-sm">
                  <option value="정기">정기</option>
                  <option value="특별">특별</option>
                  <option value="수시">수시</option>
                </select>
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">대상창고 <span class="text-danger">*</span></label>
                <select v-model="planForm.warehouse" class="form-select form-select-sm">
                  <option v-for="w in warehouseList" :key="w" :value="w">{{ w }}</option>
                </select>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label small fw-semibold">범위</label>
              <input v-model="planForm.scope" type="text" class="form-control form-control-sm" placeholder="예: 유제품 전체" />
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label small fw-semibold">예정일 <span class="text-danger">*</span></label>
                <input v-model="planForm.scheduled_date" type="date" class="form-control form-control-sm" />
              </div>
              <div class="col-6">
                <label class="form-label small fw-semibold">담당자</label>
                <select v-model="planForm.manager" class="form-select form-select-sm">
                  <option value="">선택</option>
                  <option v-for="e in employeeStore.employees" :key="e.employeeid" :value="e.employeeid">{{ e.lastname }}{{ e.firstname }}</option>
                </select>
              </div>
            </div>
            <div v-if="planError" class="alert alert-danger small py-2 mb-0">{{ planError }}</div>
          </div>
          <div class="modal-panel-footer d-flex gap-2">
            <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="showPlanModal = false">취소</button>
            <button class="btn btn-sm btn-primary flex-grow-1" :disabled="planSaving" @click="submitPlan">
              <span v-if="planSaving" class="spinner-border spinner-border-sm me-1"></span>등록
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useProcurementStore } from '@/stores/procurement'
import { useSsafyStore } from '@/stores/ssafy'
import { useInventoryStore } from '@/stores/inventory'
import { useEmployeeStore } from '@/stores/employees'
import { inventoryApi } from '@/api/inventory'

const procurementStore = useProcurementStore()
const ssafyStore = useSsafyStore()
const inventoryStore = useInventoryStore()
const employeeStore = useEmployeeStore()

const activeMain = ref('status')
const subtitle = computed(() => ({
  status: '창고별·품목별 실시간 재고 수량과 상태를 통합 조회합니다',
  count: '시스템 재고와 실물 재고를 비교하여 재고 정확도를 관리합니다',
  expiry: 'Lot별 유통기한을 관리하고 선입선출 원칙을 준수합니다',
}[activeMain.value]))

const warehouseList = ['경기물류센터', '중앙물류센터', '부산물류센터']
const WAREHOUSE_META = {
  '경기물류센터': { category: '상온', capacity: 32000 },
  '중앙물류센터': { category: '냉장', capacity: 29000 },
  '부산물류센터': { category: '냉동', capacity: 25000 },
}
// 카테고리별 평균 유통기한(일) — 실제 GoodsReceipt에는 유통기한 데이터가 없어 식품 일반 기준으로 추정
const SHELF_LIFE_DAYS = {
  '음료': 180, '조미료': 365, '제과류': 120, '유제품': 21,
  '곡물/시리얼': 270, '육류/가금류': 10, '농산물': 14, '수산물': 7,
}

// ===================== 1. 재고현황 =====================
const statusFilter = reactive({ warehouse: '', category: '' })

const passReceipts = computed(() => procurementStore.goodsReceipts.filter((g) => g.qcstatus === 'pass'))

const warehouseRows = computed(() => {
  return warehouseList.map((w) => {
    const meta = WAREHOUSE_META[w]
    const stock = passReceipts.value.filter((g) => g.warehouse === w).reduce((s, g) => s + g.quantityreceived, 0)
    // 출고예정: 실제 창고별 출고 데이터가 없어 현재고의 일부를 결정론적으로 추정
    const outbound = Math.round(stock * (0.04 + (w.length % 3) * 0.015))
    return {
      warehouse: w,
      category: meta.category,
      capacity: meta.capacity,
      stock,
      available: stock - outbound,
      outbound,
      rate: meta.capacity ? (stock / meta.capacity) * 100 : 0,
    }
  })
})

const filteredWarehouseRows = computed(() => {
  let list = warehouseRows.value
  if (statusFilter.warehouse) list = list.filter((r) => r.warehouse === statusFilter.warehouse)
  if (statusFilter.category) list = list.filter((r) => r.category === statusFilter.category)
  return list
})

function rateStatus(rate) {
  if (rate > 100) return '초과'
  if (rate >= 90) return '긴급'
  if (rate >= 75) return '주의'
  return '정상'
}
function rateBarClass(rate) {
  if (rate > 100) return 'bg-danger'
  if (rate >= 90) return 'bg-danger'
  if (rate >= 75) return 'bg-warning'
  return 'bg-success'
}
function statusMeta(label) {
  const map = {
    '정상': { cls: 'bg-success-subtle text-success border border-success-subtle' },
    '주의': { cls: 'bg-warning-subtle text-warning border border-warning-subtle' },
    '긴급': { cls: 'bg-danger-subtle text-danger border border-danger-subtle' },
    '초과': { cls: 'bg-danger-subtle text-danger border border-danger-subtle' },
  }
  return map[label] || { cls: 'bg-secondary-subtle text-secondary' }
}

const statusKpi = computed(() => {
  const rows = warehouseRows.value
  const belowSafety = ssafyStore.products.filter((p) => p.unitsinstock < p.reorderlevel).length
  return {
    totalStock: rows.reduce((s, r) => s + r.stock, 0),
    available: rows.reduce((s, r) => s + r.available, 0),
    overCapacity: rows.filter((r) => r.rate > 100).length,
    belowSafety,
  }
})

// ===================== 2. 재고실사 =====================
const countTab = ref('plan')
const planFilter = reactive({ type: '', status: '' })

const filteredPlans = computed(() => {
  let list = inventoryStore.countPlans
  if (planFilter.type) list = list.filter((p) => p.count_type === planFilter.type)
  if (planFilter.status) list = list.filter((p) => p.status === planFilter.status)
  return list
})

function planStatusMeta(status) {
  const map = {
    '대기': { cls: 'bg-warning-subtle text-warning border border-warning-subtle' },
    '진행중': { cls: 'bg-primary-subtle text-primary border border-primary-subtle' },
    '완료': { cls: 'bg-success-subtle text-success border border-success-subtle' },
  }
  return map[status] || { cls: 'bg-secondary-subtle text-secondary' }
}

const allCountItems = computed(() => inventoryStore.countPlans.flatMap((p) => p.items.map((it) => ({ ...it, planCode: p.code, planId: p.id }))))

const countKpi = computed(() => {
  const now = new Date()
  const monthly = inventoryStore.countPlans.filter((p) => {
    const d = new Date(p.scheduled_date)
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
  }).length
  const total = inventoryStore.countPlans.length
  const completed = inventoryStore.countPlans.filter((p) => p.status === '완료').length
  const counted = allCountItems.value.filter((it) => it.counted_qty != null)
  const matched = counted.filter((it) => it.diff === 0)
  return {
    monthly,
    completionRate: total ? (completed / total) * 100 : 0,
    matchRate: counted.length ? (matched.length / counted.length) * 100 : 0,
    diffCount: counted.filter((it) => it.diff !== 0).length,
  }
})

const diffRows = computed(() => allCountItems.value.filter((it) => it.counted_qty != null && it.diff !== 0))

// 실사등록
const registerPlanId = ref('')
const itemEdits = reactive({})
const newItemProductId = ref('')

const selectedPlan = computed(() => inventoryStore.countPlans.find((p) => p.id === registerPlanId.value) || null)

watch(selectedPlan, (plan) => {
  if (!plan) return
  plan.items.forEach((it) => { itemEdits[it.id] = it.counted_qty ?? it.system_qty })
}, { immediate: true })

function diffClass(counted, system) {
  if (counted == null) return ''
  const d = counted - system
  if (d === 0) return 'text-muted'
  return d > 0 ? 'text-success' : 'text-danger'
}

async function saveCountItem(item) {
  try {
    await inventoryApi.updateCountItem(item.id, { counted_qty: itemEdits[item.id] })
    await inventoryStore.fetchAll()
  } catch {
    alert('저장에 실패했습니다.')
  }
}

async function addCountItem() {
  if (!registerPlanId.value || !newItemProductId.value) return
  const product = ssafyStore.products.find((p) => p.productid === newItemProductId.value)
  try {
    await inventoryApi.createCountItem({
      plan: registerPlanId.value,
      product: newItemProductId.value,
      system_qty: product?.unitsinstock || 0,
    })
    newItemProductId.value = ''
    await inventoryStore.fetchAll()
  } catch {
    alert('품목 추가에 실패했습니다.')
  }
}

// 실사계획 등록 모달
const showPlanModal = ref(false)
const planSaving = ref(false)
const planError = ref('')
const planForm = reactive({ count_type: '정기', warehouse: warehouseList[0], scope: '', scheduled_date: '', manager: '' })

function openPlanModal() {
  planForm.count_type = '정기'
  planForm.warehouse = warehouseList[0]
  planForm.scope = ''
  planForm.scheduled_date = ''
  planForm.manager = ''
  planError.value = ''
  showPlanModal.value = true
}

async function submitPlan() {
  if (!planForm.warehouse || !planForm.scheduled_date) {
    planError.value = '대상창고와 예정일을 입력하세요.'
    return
  }
  planSaving.value = true
  planError.value = ''
  try {
    const payload = { ...planForm, status: '대기' }
    if (!payload.manager) delete payload.manager
    await inventoryApi.createCountPlan(payload)
    showPlanModal.value = false
    await inventoryStore.fetchAll()
  } catch (e) {
    planError.value = e?.response?.data ? JSON.stringify(e.response.data) : '등록에 실패했습니다.'
  } finally {
    planSaving.value = false
  }
}

// ===================== 3. 유통기한관리 =====================
const expiryTab = ref('all')
const expiryFilter = reactive({ category: '', warehouse: '', name: '' })
function resetExpiryFilter() {
  expiryFilter.category = ''
  expiryFilter.warehouse = ''
  expiryFilter.name = ''
}

const productMap = computed(() => new Map(ssafyStore.products.map((p) => [p.productid, p])))

// 데이터셋의 최신 입고일을 "기준일"로 사용 (실제 데이터가 과거~현재 분산되어 있어 시스템 날짜 대신 사용)
const anchorDate = computed(() => {
  let max = null
  passReceipts.value.forEach((g) => { if (!max || g.receiptdate > max) max = g.receiptdate })
  return max ? new Date(max) : new Date()
})

// 실제로는 유통기한이 훨씬 지난 과거 입고분은 이미 소비/폐기되어 더는 실물 재고로 존재하지 않을
// 것이므로, "최근 90일 이내에 기한이 지난" 것까지만 현재 추적 대상 Lot으로 간주한다.
const EXPIRED_GRACE_DAYS = 90

const lots = computed(() => {
  const productMapV = productMap.value
  return passReceipts.value
    .map((g) => {
      const product = productMapV.get(g.productid)
      const categoryName = product?.category_name || '기타'
      const shelfDays = SHELF_LIFE_DAYS[categoryName] || 90
      const manufactureDate = new Date(g.receiptdate)
      const expiryDate = new Date(manufactureDate.getTime() + shelfDays * 86400000)
      const remainingDays = Math.round((expiryDate - anchorDate.value) / 86400000)
      let lotStatus = 'normal'
      if (remainingDays < 0) lotStatus = 'expired'
      else if (remainingDays <= 7) lotStatus = 'critical'
      else if (remainingDays <= 30) lotStatus = 'warning'
      return {
        id: g.id,
        productid: g.productid,
        productName: g.product_name || product?.productname || '-',
        categoryName,
        lotNumber: `LOT-${String(g.id).padStart(6, '0')}`,
        warehouse: g.warehouse,
        manufactureDate: g.receiptdate,
        expiryDate: expiryDate.toISOString().slice(0, 10),
        remainingDays,
        quantity: g.quantityreceived,
        status: lotStatus,
      }
    })
    .filter((lot) => lot.remainingDays >= -EXPIRED_GRACE_DAYS)
})

const expiryKpi = computed(() => {
  const list = lots.value
  return {
    expired: list.filter((l) => l.status === 'expired').length,
    critical: list.filter((l) => l.status === 'critical').length,
    warning: list.filter((l) => l.status === 'warning').length,
    normal: list.filter((l) => l.status === 'normal').length,
  }
})

const filteredLots = computed(() => {
  let list = lots.value
  if (expiryFilter.category) list = list.filter((l) => l.categoryName === expiryFilter.category)
  if (expiryFilter.warehouse) list = list.filter((l) => l.warehouse === expiryFilter.warehouse)
  if (expiryFilter.name) {
    const q = expiryFilter.name.toLowerCase()
    list = list.filter((l) => l.productName.toLowerCase().includes(q))
  }
  if (expiryTab.value === 'd30') list = list.filter((l) => l.remainingDays >= 0 && l.remainingDays <= 30)
  else if (expiryTab.value === 'expired') list = list.filter((l) => l.status === 'expired')
  return list
})

const sortedLots = computed(() => {
  const list = [...filteredLots.value]
  if (expiryTab.value === 'fifo') list.sort((a, b) => (a.expiryDate > b.expiryDate ? 1 : -1))
  else list.sort((a, b) => (a.remainingDays > b.remainingDays ? 1 : -1))
  return list
})

const lotPage = ref(1)
const lotPageSize = 15
const lotPageStart = computed(() => (lotPage.value - 1) * lotPageSize)
const lotPageEnd = computed(() => Math.min(sortedLots.value.length, lotPageStart.value + lotPageSize))
const lotTotalPages = computed(() => Math.max(1, Math.ceil(sortedLots.value.length / lotPageSize)))
const pagedLots = computed(() => sortedLots.value.slice(lotPageStart.value, lotPageEnd.value))

watch([expiryTab, () => expiryFilter.category, () => expiryFilter.warehouse, () => expiryFilter.name], () => { lotPage.value = 1 })

function expiryStatusMeta(status) {
  const map = {
    expired: { label: '기한경과', cls: 'bg-danger-subtle text-danger border border-danger-subtle' },
    critical: { label: '긴급', cls: 'bg-danger-subtle text-danger border border-danger-subtle' },
    warning: { label: '임박', cls: 'bg-warning-subtle text-warning border border-warning-subtle' },
    normal: { label: '정상', cls: 'bg-success-subtle text-success border border-success-subtle' },
  }
  return map[status] || { label: status, cls: 'bg-secondary-subtle text-secondary' }
}
function processLot(lot) {
  alert(`${lot.productName} (${lot.lotNumber}) 처리 등록되었습니다.`)
}

onMounted(() => {
  procurementStore.fetchAll()
  ssafyStore.fetchProducts()
  ssafyStore.fetchCategories()
  inventoryStore.fetchAll()
  employeeStore.fetchAll()
})
</script>

<style scoped>
.erp-card { border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.erp-card .card-footer { border-top: 1px solid #f1f5f9; border-radius: 0 0 12px 12px; }
.view-tabs { border-bottom: 1px solid #e5e7eb; }
.tab-item {
  padding: 8px 4px 10px; font-weight: 600; font-size: 0.92rem; color: #94a3b8;
  cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px;
}
.tab-item.active { color: #2563eb; border-bottom-color: #2563eb; }
.tab-item:hover { color: #2563eb; }

.modal-backdrop-custom {
  position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4);
  display: flex; align-items: center; justify-content: center; z-index: 1300;
}
.modal-panel {
  max-height: 88vh; background: #fff; border-radius: 14px;
  display: flex; flex-direction: column; overflow: hidden;
}
.modal-panel-header {
  padding: 14px 16px; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #f1f5f9; background: #fff;
}
.btn-close-panel { border: none; background: transparent; color: #94a3b8; font-size: 0.9rem; cursor: pointer; }
.btn-close-panel:hover { color: #374151; }
.modal-panel-body { flex: 1; overflow-y: auto; padding: 16px; }
.modal-panel-footer { padding: 12px 16px; border-top: 1px solid #f1f5f9; }
</style>
