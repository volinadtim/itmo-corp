# Карта my.itmo.ru

Сгенерировано `scripts/crawl-sitemap.mjs` 2026-10-01 (с живой проверкой GET под учёткой студента). Источник — публичный фронтенд-бандл и API портала; обновить: `npm run crawl:probe` в `integrations/my-itmo/mcp-server`.

## Сайты

- **my.itmo.ru** — Student personal cabinet (Nuxt SPA + /api JSON, ITMO ID Bearer auth)
- **id.itmo.ru** — ITMO ID — Keycloak realm 'itmo' (OIDC provider)
- **itmo.ru/ru/schedule** — Public timetable by teacher / group / room (server-rendered HTML, no login)
- **isu.ifmo.ru** — Legacy ISU portal (not covered by the MCP)
- **abit.itmo.ru** — Admissions portal (not covered by the MCP)
- **helpdesk.itmo.ru** — Support desk (Jira Service Management)

## Страницы (SPA-маршруты)

| Путь | Имя |
|---|---|
| `/` | index |
| `/assistant` | assistant |
| `/certifications/admin/chairmans` | certifications-admin-chairmans |
| `/certifications/admin/chairmans/composition/:composition?` | certifications-admin-chairmans-composition-composition |
| `/certifications/admin/chairmans/schedule/:schedule` | certifications-admin-chairmans-schedule-schedule |
| `/certifications/admin/chairmans/schedule/:schedule?/students/:student?` | certifications-admin-chairmans-schedule-schedule-students-student |
| `/certifications/admin/diploma` | certifications-admin-diploma |
| `/certifications/admin/diploma/:certification` | certifications-admin-diploma-certification |
| `/certifications/admin/diploma/:certification/history` | certifications-admin-diploma-certification-history |
| `/certifications/admin/experts` | certifications-admin-experts |
| `/certifications/admin/orders` | certifications-admin-orders |
| `/certifications/admin/orders/:order` | certifications-admin-orders-order |
| `/certifications/admin/print` | certifications-admin-print |
| `/certifications/admin/reviewers` | certifications-admin-reviewers |
| `/certifications/admin/secretaries` | certifications-admin-secretaries |
| `/certifications/admin/supplement` | certifications-admin-supplement |
| `/certifications/admin/supplement/:supplement` | certifications-admin-supplement-supplement |
| `/certifications/admin/supplement/:supplement/history` | certifications-admin-supplement-supplement-history |
| `/certifications/admin/supplement/eu` | certifications-admin-supplement-eu |
| `/certifications/admin/supplement/eu/:supplement` | certifications-admin-supplement-eu-supplement |
| `/certifications/diploma` | certifications-diploma |
| `/certifications/diploma/:diploma` | certifications-diploma-diploma |
| `/constructor/kug` | constructor-kug |
| `/constructor/kug/:kug` | constructor-kug-kug |
| `/constructor/modules` | constructor-modules |
| `/constructor/modules/:module` | constructor-modules-module |
| `/constructor/programs` | constructor-programs |
| `/constructor/programs/:program` | constructor-programs-program |
| `/election` | election |
| `/election/facultative` | election-facultative |
| `/employment` | employment |
| `/employment/:id` | employment-id |
| `/employment/archive` | employment-archive |
| `/finances` | finances |
| `/intro` | intro |
| `/login` | login |
| `/login/callback` | login-callback |
| `/persons` | persons |
| `/persons/:person?` | persons-person |
| `/plan` | plan |
| `/plans` | plans |
| `/plans/:id` | plans-id |
| `/points` | points |
| `/practices` | practices |
| `/practices/:practice` | practices-practice |
| `/programs` | programs |
| `/programs/:program` | programs-program |
| `/readyz` | readyz |
| `/requests` | requests-index |
| `/requests/v2` | requests-v2 |
| `/schedule` | schedule |
| `/search` | search |
| `/services` | services |
| `/services/adviser` | services-adviser |
| `/services/adviser/:person` | services-adviser-person |
| `/services/agreements` | services-agreements |
| `/services/booking` | services-booking |
| `/services/booking/group/:group?` | services-booking-group-group |
| `/services/booking/my` | services-booking-my |
| `/services/checklist` | services-checklist |
| `/services/dormitories` | services-dormitories |
| `/services/health` | services-health |
| `/services/navigator` | services-navigator |
| `/sport` | sport |
| `/sport/sign` | sport-sign |
| `/vacation` | vacation |
| `/vacation/management` | vacation-management |

## Меню (для текущей учётки)

- `/` — menu.home
- `/schedule` — menu.schedule
- `/points` — modules.record_book.title
- `/plan` — modules.eduPlan.page.menu
- `/election` — menu.election
  - `/election` — modules.election.name
  - `/election/facultative` — modules.electionFacultative.menu
- `/sport` — Спорт
  - `/sport` — Мой спорт
  - `/sport/sign` — Запись на секции
- `/practices` — modules.practices.title
- `/finances` — menu.finances
- `/persons` — modules.personalities.title
- `/requests` — modules.requests.requestsAndQueues
- `/services` — menu.services

### Сервисы

- `/services/navigator` — Карта корпусов и построение маршрутов
- `/services/dormitories` — Заселение и проживание
- `/services/agreements` — Подписание соглашений
- `/services/booking` — Бронирование помещений
- `/plans` — Индивидуальные учебные планы
- `/programs` — Рабочие программы
- `/constructor/programs` — Образовательные программы
- `/certifications/admin/diploma` — Отзыв рецензента

## API по модулям

`/api/<module>/…`, авторизация `Authorization: Bearer <ITMO ID access token>`. Аудитория: **student** — доступно студенту; **mixed** — зависит от роли; **adviser/staff** — сотрудники (MCP их не использует). Статус — результат последней живой проверки GET (200 работает, 403 закрыто для этой учётки сейчас).

### agreements (student, 4)

MCP: itmo_student_info (agreements) — read only

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/agreements/agreements` |  |  | 200 |
| GET | `/api/agreements/agreements/{id}/{id}/download` |  |  |  |
| POST | `/api/agreements/agreements/{id}/sign` |  | legal |  |
| POST | `/api/agreements/agreements/sign-batch` |  | legal |  |

### booking (student, 13)

MCP: itmo_student_info (booking_*)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| PATCH | `/api/booking/bookings/` |  |  |  |
| POST | `/api/booking/bookings/` |  |  |  |
| DELETE | `/api/booking/bookings/{booking_id}` |  |  |  |
| GET | `/api/booking/bookings/my` |  |  | 500 |
| GET | `/api/booking/bookings/statuses` |  |  | 500 |
| GET | `/api/booking/dictionary/rooms/categories` |  |  | 200 |
| GET | `/api/booking/dictionary/rooms/categories?groupId={id}` |  |  |  |
| GET | `/api/booking/dictionary/rooms/groups` |  |  | 500 |
| GET | `/api/booking/rooms/byName` | search |  |  |
| GET | `/api/booking/rooms/roomBookings` |  |  | 500 |
| GET | `/api/booking/rooms/roomsInCategory` |  |  | 422 |
| GET | `/api/booking/users/event/mostPopular` | counts |  |  |
| GET | `/api/booking/users/status` |  |  | 200 |

### constructor (staff, 100)

MCP: function Object() { [native code] }

Служебный модуль, эндпоинты см. в `data/api-catalog.json`.

### constructor-ep (staff, 112)

Служебный модуль, эндпоинты см. в `data/api-catalog.json`.

### dms (student, 13)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/dms/citizenships` |  |  | 200 |
| GET | `/api/dms/filters/statuses` |  |  | 200 |
| GET | `/api/dms/me/access` |  |  | 200 |
| POST | `/api/dms/me/corp_mail` |  |  |  |
| GET | `/api/dms/me/request` |  |  | 200 |
| POST | `/api/dms/me/request/{request_id}` |  |  |  |
| POST | `/api/dms/me/request/{request_id}/reject` |  | approval |  |
| POST | `/api/dms/me/request/{request_id}/sign` |  |  |  |
| GET | `/api/dms/me/request/contacts` |  |  | 200 |
| GET | `/api/dms/request/{request_id}/files/{user_file_name}` |  |  |  |
| GET | `/api/dms/request/list` |  |  | 403 |
| GET | `/api/dms/request/list/{id}` |  |  |  |
| POST | `/api/dms/request/me/{request_id}/decision` |  |  |  |

### dormitory (student, 11)

MCP: itmo_student_info (dormitory_*)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/dormitory/apartments` |  |  | 200 |
| GET | `/api/dormitory/documents` |  |  | 200 |
| GET | `/api/dormitory/payments/contracts?from={dateFrom}&to={dateTo}` |  |  |  |
| GET | `/api/dormitory/payments/contracts/periods` |  |  |  |
| POST | `/api/dormitory/payments/pay` |  | financial |  |
| DELETE | `/api/dormitory/settlement/cancel` |  | housing |  |
| POST | `/api/dormitory/settlement/change_category` |  | housing |  |
| POST | `/api/dormitory/settlement/register` |  | housing |  |
| DELETE | `/api/dormitory/settlement/remove` |  | housing |  |
| GET | `/api/dormitory/settlement/slots` |  | housing | 200 |
| GET | `/api/dormitory/status/full` |  |  | 200 |

### eduPlan (student, 7)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| DELETE | `/api/eduPlan/{id}/modules/{moduleId}/disciplines/{disciplineId}/sign` |  |  |  |
| POST | `/api/eduPlan/{id}/modules/{moduleId}/disciplines/{disciplineId}/sign` |  |  |  |
| DELETE | `/api/eduPlan/{id}/modules/{moduleId}/disciplines/{id}/sign` |  |  |  |
| POST | `/api/eduPlan/{planId}/modules/{moduleId}/disciplines/{discId}/replace/{id}` |  |  |  |
| GET | `/api/eduPlan/{planId}/modules/{moduleId}/disciplines/{id}/replaceable` |  |  |  |
| DELETE | `/api/eduPlan/{planId}/replace/{id}` |  |  |  |
| GET | `/api/eduPlan/{planId}/replaceable_discs` |  |  |  |

### election (student, 15)

MCP: itmo_student_info (election_*)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/election/students/availability` |  |  | 200 |
| GET | `/api/election/students/available_disciplines` |  |  | 403 |
| GET | `/api/election/students/chosen_flows` |  |  | 403 |
| POST | `/api/election/students/group_flow_available_disciplines` |  |  |  |
| GET | `/api/election/students/limits/flow_groups` |  |  | 403 |
| GET | `/api/election/students/limits/flows` |  |  | 403 |
| POST | `/api/election/students/order/` |  |  |  |
| POST | `/api/election/students/order/change` |  |  |  |
| POST | `/api/election/students/order/clear` |  |  |  |
| GET | `/api/election/students/ordered_flow_chains` |  |  | 403 |
| GET | `/api/election/students/schedule/base/timeline` | date_start, date_end |  |  |
| POST | `/api/election/students/schedule/combined?date_start={dateStart}&date_end={dateEnd}` |  |  |  |
| GET | `/api/election/students/schedule/flows/{id}/timeline` | date_start, date_end |  |  |
| POST | `/api/election/students/schedule/flows/intersections` |  |  |  |
| GET | `/api/election/students/selected_flow_chains` |  |  | 200 |

### employments (staff, 27)

Служебный модуль, эндпоинты см. в `data/api-catalog.json`.

### facultative (student, 14)

MCP: itmo_student_info (facultative_status)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| POST | `/api/facultative/booking/` |  |  |  |
| POST | `/api/facultative/commit/` |  |  |  |
| GET | `/api/facultative/current/` |  |  | 403 |
| GET | `/api/facultative/current/{isu}` |  |  |  |
| GET | `/api/facultative/description/` |  |  | 200 |
| GET | `/api/facultative/description/start/` |  |  | 200 |
| GET | `/api/facultative/json/` |  |  | 403 |
| GET | `/api/facultative/json/{isu}` |  |  |  |
| GET | `/api/facultative/limits/` |  |  | 403 |
| GET | `/api/facultative/limits/{id}` |  |  |  |
| GET | `/api/facultative/schedule/flow/{flowId}/` |  |  |  |
| GET | `/api/facultative/schedule/flow/{id}/` |  |  |  |
| GET | `/api/facultative/schedule/user/` |  |  | 403 |
| GET | `/api/facultative/status/` |  |  | 200 |

### finances (student, 15)

MCP: itmo_finances

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/finances/edupayments/availability` |  |  | 200 |
| GET | `/api/finances/edupayments/contracts` |  |  | 200 |
| GET | `/api/finances/edupayments/payments` |  |  |  |
| POST | `/api/finances/edupayments/payments/pay` |  | financial |  |
| GET | `/api/finances/salary/current` |  |  | 200 |
| GET | `/api/finances/salary/payouts` |  |  |  |
| GET | `/api/finances/salary/payouts/last` |  |  |  |
| GET | `/api/finances/salary/payouts/month` | month, year |  |  |
| GET | `/api/finances/salary/payouts/total` |  |  |  |
| GET | `/api/finances/salary/payouts/total?dateFrom={id}&dateTo={id}` |  |  |  |
| GET | `/api/finances/salary/year` | year |  |  |
| GET | `/api/finances/scholarship/account` |  |  | 200 |
| GET | `/api/finances/scholarship/income` |  |  | 200 |
| GET | `/api/finances/scholarship/total` |  |  | 200 |
| GET | `/api/finances/scholarship/total?dateFrom={id}&dateTo={id}` |  |  |  |

### gia (staff, 152)

Служебный модуль, эндпоинты см. в `data/api-catalog.json`.

### gia-students (student, 42)

MCP: itmo_student_info (diplomas_mine)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| DELETE | `/api/gia-students/attachment/{diplomaId}/eu` |  |  |  |
| POST | `/api/gia-students/attachment/{diplomaId}/eu/init_payment` |  |  |  |
| GET | `/api/gia-students/attachment/{id}` |  |  |  |
| GET | `/api/gia-students/attachment/{id}/eu` |  |  |  |
| POST | `/api/gia-students/attachment/{id}/eu` |  |  |  |
| POST | `/api/gia-students/attachment/{id}/eu/approve` |  | approval |  |
| POST | `/api/gia-students/attachment/{id}/eu/rollback` |  |  |  |
| POST | `/api/gia-students/attachment/approve/{id}/{id}` |  | approval |  |
| POST | `/api/gia-students/diplomas/{diploma}/agreement` |  |  |  |
| PUT | `/api/gia-students/diplomas/{diploma}/annotation` |  |  |  |
| PUT | `/api/gia-students/diplomas/{diploma}/application` |  |  |  |
| PUT | `/api/gia-students/diplomas/{diploma}/file` |  |  |  |
| GET | `/api/gia-students/diplomas/{diploma}/file/antiplagiat/report` |  |  |  |
| GET | `/api/gia-students/diplomas/{diploma}/file/download/{key}` |  |  |  |
| GET | `/api/gia-students/diplomas/{diploma}/file/download/{result_file_key}` |  |  |  |
| POST | `/api/gia-students/diplomas/{diploma}/presentation/extra-files` |  |  |  |
| DELETE | `/api/gia-students/diplomas/{diploma}/presentation/extra-files/{file_key}` |  |  |  |
| PUT | `/api/gia-students/diplomas/{diploma}/presentation/file` |  |  |  |
| DELETE | `/api/gia-students/diplomas/{diploma}/presentations/{presentation_id}/signup` |  |  |  |
| POST | `/api/gia-students/diplomas/{diploma}/presentations/{presentation_id}/signup` |  |  |  |
| DELETE | `/api/gia-students/diplomas/{diploma}/revoke` | stage |  |  |
| PUT | `/api/gia-students/diplomas/{diploma}/task` |  |  |  |
| GET | `/api/gia-students/diplomas/{id}/annotation` |  |  |  |
| GET | `/api/gia-students/diplomas/{id}/application` |  |  |  |
| GET | `/api/gia-students/diplomas/{id}/file` |  |  |  |
| GET | `/api/gia-students/diplomas/{id}/info` |  |  |  |
| GET | `/api/gia-students/diplomas/{id}/presentation` |  |  |  |
| GET | `/api/gia-students/diplomas/{id}/presentations/possible` |  |  |  |
| GET | `/api/gia-students/diplomas/{id}/task` |  |  |  |
| GET | `/api/gia-students/diplomas/my` |  |  | 200 |
| GET | `/api/gia-students/me/grants` |  |  | 200 |
| GET | `/api/gia-students/me/publications` |  |  | 200 |
| GET | `/api/gia-students/me/speeches` |  |  | 200 |
| GET | `/api/gia-students/people` |  |  | 200 |
| GET | `/api/gia-students/people/` |  |  | 404 |
| GET | `/api/gia-students/references/academic-titles` |  |  | 200 |
| GET | `/api/gia-students/references/agreement` |  |  | 500 |
| GET | `/api/gia-students/references/degree-types` |  |  | 200 |
| GET | `/api/gia-students/references/diploma-types` |  |  | 200 |
| GET | `/api/gia-students/references/organization-statuses` |  |  | 404 |
| GET | `/api/gia-students/references/statuses` | entity |  |  |
| GET | `/api/gia-students/users/status` |  |  | 404 |

### individual-plan (student, 35)

MCP: itmo_student_info (individual_plan_*)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/individual-plan/flags` |  |  | 200 |
| GET | `/api/individual-plan/plan` |  |  | 403 |
| POST | `/api/individual-plan/plan` |  |  |  |
| GET | `/api/individual-plan/plan/{id}` |  |  |  |
| GET | `/api/individual-plan/plan/{id}/availableDisciplines` |  |  |  |
| GET | `/api/individual-plan/plan/{id}/changes` |  |  |  |
| GET | `/api/individual-plan/plan/{id}/discipline/{id}/use` | draft |  |  |
| DELETE | `/api/individual-plan/plan/{id}/draft` |  |  |  |
| GET | `/api/individual-plan/plan/{id}/draft` |  |  |  |
| POST | `/api/individual-plan/plan/{id}/draft` |  |  |  |
| POST | `/api/individual-plan/plan/{id}/draft/save` |  |  |  |
| GET | `/api/individual-plan/plan/{id}/lowerModules` |  |  |  |
| POST | `/api/individual-plan/plan/{id}/module` |  |  |  |
| DELETE | `/api/individual-plan/plan/{id}/module/{id}` |  |  |  |
| PATCH | `/api/individual-plan/plan/{id}/module/{id}` |  |  |  |
| POST | `/api/individual-plan/plan/{id}/module/{id}/discipline` |  |  |  |
| DELETE | `/api/individual-plan/plan/{id}/module/{id}/discipline/{id}` |  |  |  |
| PATCH | `/api/individual-plan/plan/{id}/module/{id}/discipline/{id}` |  |  |  |
| DELETE | `/api/individual-plan/plan/{id}/module/{id}/discipline/{id}/choice` |  |  |  |
| PATCH | `/api/individual-plan/plan/{id}/module/{id}/discipline/{id}/choice` |  |  |  |
| POST | `/api/individual-plan/plan/{id}/module/{id}/discipline/{id}/choice` |  |  |  |
| PATCH | `/api/individual-plan/plan/{id}/module/{id}/discipline/{id}/flowChoice` |  |  |  |
| PATCH | `/api/individual-plan/plan/{id}/module/{id}/discipline/{id}/move` |  |  |  |
| GET | `/api/individual-plan/plan/{id}/plan` |  |  |  |
| POST | `/api/individual-plan/plan/{id}/plan/validate/personal-plan-content` |  |  |  |
| POST | `/api/individual-plan/plan/{id}/plan/validate/plan-content` |  |  |  |
| POST | `/api/individual-plan/plan/{id}/plan/validate/selection` |  |  |  |
| GET | `/api/individual-plan/plan/{id}/semesters` |  |  |  |
| GET | `/api/individual-plan/plan/{id}/upperModules` |  |  |  |
| GET | `/api/individual-plan/plan/directions` |  |  | 200 |
| GET | `/api/individual-plan/plan/implementers` |  |  | 200 |
| GET | `/api/individual-plan/plan/programs` |  |  | 200 |
| GET | `/api/individual-plan/plan/role` |  |  | 200 |
| GET | `/api/individual-plan/plan/statuses` |  |  | 200 |
| GET | `/api/individual-plan/semesters/current` |  |  | 200 |

### intro (student, 14)

MCP: itmo_student_info (intro_status)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| POST | `/api/intro/booking/` |  |  |  |
| POST | `/api/intro/commit/` |  |  |  |
| GET | `/api/intro/current/` |  |  | 403 |
| GET | `/api/intro/current/{isu}` |  |  |  |
| GET | `/api/intro/description/` |  |  | 404 |
| GET | `/api/intro/description/start/` |  |  | 404 |
| GET | `/api/intro/json/` |  |  | 403 |
| GET | `/api/intro/json/{isu}` |  |  |  |
| GET | `/api/intro/limits/` |  |  | 403 |
| GET | `/api/intro/limits/{id}` |  |  |  |
| GET | `/api/intro/schedule/flow/{flowId}/` |  |  |  |
| GET | `/api/intro/schedule/flow/{id}/` |  |  |  |
| GET | `/api/intro/schedule/user/` |  |  | 403 |
| GET | `/api/intro/status/` |  |  | 200 |

### personalities (student, 3)

MCP: itmo_people_search

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/personalities/persons` | offset, limit, q |  |  |
| GET | `/api/personalities/persons/{id}` |  |  |  |
| GET | `/api/personalities/persons/{id}/activities` |  |  |  |

### practices (student, 20)

MCP: itmo_student_info (practices_programs)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/practices/feedback/head?id={id}` |  |  |  |
| GET | `/api/practices/ind_task?id={id}` |  |  |  |
| POST | `/api/practices/ind_task/approve` |  | approval |  |
| DELETE | `/api/practices/ind_task/cancel` |  |  |  |
| POST | `/api/practices/ind_task/create` |  |  |  |
| PUT | `/api/practices/ind_task/create` |  |  |  |
| POST | `/api/practices/ind_task/stage/add` |  |  |  |
| DELETE | `/api/practices/ind_task/stage/delete` |  |  |  |
| PUT | `/api/practices/ind_task/stage/update` |  |  |  |
| GET | `/api/practices/practices?id={id}` |  |  |  |
| POST | `/api/practices/practices/{id}/application` |  |  |  |
| GET | `/api/practices/practices/all` | op_id, current |  |  |
| GET | `/api/practices/practices/op` |  |  | 200 |
| GET | `/api/practices/report?id={id}` |  |  |  |
| POST | `/api/practices/report/approve` |  | approval |  |
| POST | `/api/practices/report/create` |  |  |  |
| GET | `/api/practices/report/emp_stats` |  |  | 200 |
| GET | `/api/practices/report/grades` |  |  | 200 |
| GET | `/api/practices/report/types` |  |  | 200 |
| PUT | `/api/practices/report/update` |  |  |  |

### queues (student, 6)

MCP: itmo_student_info (queues_*)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| DELETE | `/api/queues/` |  |  |  |
| GET | `/api/queues/` | table_id, type_id |  |  |
| POST | `/api/queues/` |  |  |  |
| GET | `/api/queues/archive` |  |  | 200 |
| GET | `/api/queues/current` |  |  | 200 |
| GET | `/api/queues/slots` | table_id, type_id |  |  |

### record_book (student, 3)

MCP: itmo_record_book

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/record_book/{currentPlan}/{currentSemester}` |  |  |  |
| GET | `/api/record_book/{id}` |  |  |  |
| GET | `/api/record_book/specializations` |  |  | 200 |

### requests (student/staff/mixed, 63)

MCP: itmo_requests, itmo_request_*

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/requests/{requestId}` |  |  |  |
| GET | `/api/requests/all` |  |  | 200 |
| GET | `/api/requests/dict/{dictId}` |  |  |  |
| POST | `/api/requests/form_update` |  |  |  |
| GET | `/api/requests/my` |  |  | 200 |
| DELETE | `/api/requests/my/{requestId}` |  |  |  |
| GET | `/api/requests/my/{requestId}` |  |  |  |
| GET | `/api/requests/my/{requestId}/download` |  |  |  |
| POST | `/api/requests/send` |  |  |  |
| GET | `/api/requests/v2/access-definitions` |  |  |  |
| PUT | `/api/requests/v2/access-definitions` |  |  |  |
| GET | `/api/requests/v2/access-definitions/{code}/users` |  |  |  |
| PUT | `/api/requests/v2/access-definitions/{code}/users` |  |  |  |
| DELETE | `/api/requests/v2/access-definitions/{selectedCode}` |  |  |  |
| POST | `/api/requests/v2/access-definitions/{selectedCode}/refresh` |  |  |  |
| GET | `/api/requests/v2/access-definitions/admin-access` |  |  |  |
| GET | `/api/requests/v2/access-definitions/options` |  |  |  |
| POST | `/api/requests/v2/access-definitions/test` |  |  |  |
| GET | `/api/requests/v2/admin/process-instances` | status, search, page, size |  |  |
| DELETE | `/api/requests/v2/admin/process-instances/{id}` |  |  |  |
| GET | `/api/requests/v2/admin/process-instances/{id}` |  |  |  |
| POST | `/api/requests/v2/admin/process-instances/{id}/activities/{activityId}/restart` |  |  |  |
| POST | `/api/requests/v2/admin/process-instances/{id}/jobs/{id}/retry` |  |  |  |
| GET | `/api/requests/v2/categories` |  |  |  |
| PUT | `/api/requests/v2/categories` |  |  |  |
| DELETE | `/api/requests/v2/categories/{id}` |  |  |  |
| GET | `/api/requests/v2/context-enrichments` |  |  |  |
| GET | `/api/requests/v2/dictionaries` |  |  | 200 |
| GET | `/api/requests/v2/dictionaries/admin` |  |  |  |
| PUT | `/api/requests/v2/dictionaries/admin` |  |  |  |
| GET | `/api/requests/v2/dictionaries/admin-access` |  |  |  |
| DELETE | `/api/requests/v2/dictionaries/admin/{selectedCode}` |  |  |  |
| POST | `/api/requests/v2/dictionaries/test` |  |  |  |
| GET | `/api/requests/v2/forms` |  |  |  |
| POST | `/api/requests/v2/forms` |  |  |  |
| GET | `/api/requests/v2/forms/{id}` |  |  |  |
| PUT | `/api/requests/v2/forms/{id}/access` |  |  |  |
| GET | `/api/requests/v2/platform-roles` |  |  |  |
| DELETE | `/api/requests/v2/platform-roles/{id}` |  |  |  |
| PUT | `/api/requests/v2/platform-roles/{userId}?role={role}` |  |  |  |
| GET | `/api/requests/v2/platform-roles/me` |  |  |  |
| GET | `/api/requests/v2/prefills` |  |  |  |
| GET | `/api/requests/v2/processes` |  |  |  |
| DELETE | `/api/requests/v2/processes/{id}` |  |  |  |
| GET | `/api/requests/v2/processes/{id}` |  |  |  |
| GET | `/api/requests/v2/processes/{id}/config` |  |  |  |
| PUT | `/api/requests/v2/processes/{id}/config` |  |  |  |
| POST | `/api/requests/v2/processes/{id}/publish` |  |  |  |
| POST | `/api/requests/v2/processes/{id}/suspend` |  |  |  |
| POST | `/api/requests/v2/processes/deploy` |  |  |  |
| POST | `/api/requests/v2/processes/draft` |  |  |  |
| POST | `/api/requests/v2/requests` |  |  |  |
| GET | `/api/requests/v2/requests/{id}` |  |  |  |
| GET | `/api/requests/v2/requests/mine` |  |  | 200 |
| GET | `/api/requests/v2/requests/my-tasks` |  |  | 200 |
| GET | `/api/requests/v2/requests/observed` | page, size, formCode, status, requestId, initiator |  |  |
| GET | `/api/requests/v2/requests/observed/types` |  |  | 200 |
| GET | `/api/requests/v2/requests/task-counts` |  |  | 200 |
| GET | `/api/requests/v2/tasks` |  |  |  |
| POST | `/api/requests/v2/tasks/{id}/complete` |  |  |  |
| GET | `/api/requests/v2/tasks/mine/by-request/{id}` |  |  |  |
| GET | `/api/requests/v2/tasks/mine/request-ids` |  |  |  |
| GET | `/api/requests/v2/users` | query, limit |  |  |

### schedule (student, 3)

MCP: itmo_schedule

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/schedule/meta/time_slots` |  |  | 200 |
| GET | `/api/schedule/schedule/personal` | date_start, date_end, subject_id |  |  |
| GET | `/api/schedule/subjects` |  |  | 404 |

### services (adviser/student, 13)

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/services/adviser/filters/course` |  |  |  |
| GET | `/api/services/adviser/filters/groups` |  |  |  |
| GET | `/api/services/adviser/filters/op` |  |  |  |
| GET | `/api/services/adviser/services/record_book/{currentPlan}/{currentSemester}?isu={id}` |  |  |  |
| GET | `/api/services/adviser/services/record_book/details?est_id={estId}&isu={isu}` |  |  |  |
| GET | `/api/services/adviser/services/record_book/specializations?isu={id}` |  |  |  |
| GET | `/api/services/adviser/services/replace/{isu}/{planId}` |  |  |  |
| GET | `/api/services/adviser/services/schedule` | date_start, date_end, isu |  |  |
| GET | `/api/services/adviser/students` |  |  |  |
| GET | `/api/services/adviser/students/{id}` |  |  |  |
| GET | `/api/services/adviser/students/{id}/activities` |  |  |  |
| GET | `/api/services/adviser/students/{isu}/scholarship` |  |  |  |
| GET | `/api/services/checklist/bypass` |  |  |  |

### sport (student, 34)

MCP: itmo_student_info (sport_*), itmo_sport_calendar

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| POST | `/api/sport/briefing/{id}/sign` |  |  |  |
| GET | `/api/sport/competitions/list` |  |  | 200 |
| GET | `/api/sport/competitions/list/limits` |  |  | 200 |
| POST | `/api/sport/personal/briefing` |  |  |  |
| GET | `/api/sport/personal/briefing/{id}/signed` |  |  |  |
| GET | `/api/sport/personal/briefing/list` |  |  | 200 |
| GET | `/api/sport/personal/calendar?date_start={dateStart}&date_end={dateEnd}` |  |  |  |
| GET | `/api/sport/personal/debt` |  |  | 200 |
| GET | `/api/sport/personal/externat` |  |  | 200 |
| GET | `/api/sport/personal/have_attempts` |  |  | 200 |
| GET | `/api/sport/personal/health_level` |  |  | 200 |
| GET | `/api/sport/personal/open_form?section={id}` |  |  |  |
| GET | `/api/sport/personal/open_form/ranks` |  |  | 200 |
| GET | `/api/sport/personal/score` | semester_id |  |  |
| GET | `/api/sport/personal/selections` |  |  | 200 |
| GET | `/api/sport/personal/sign_attempts` |  |  | 200 |
| GET | `/api/sport/projects/list` |  |  | 200 |
| GET | `/api/sport/semesters/current` |  |  | 200 |
| GET | `/api/sport/semesters/list` |  |  | 200 |
| GET | `/api/sport/sign/chosen` |  |  | 200 |
| DELETE | `/api/sport/sign/competitions/{id}` |  |  |  |
| POST | `/api/sport/sign/competitions/{id}` |  |  |  |
| DELETE | `/api/sport/sign/projects/{id}` |  |  |  |
| POST | `/api/sport/sign/projects/{id}` |  |  |  |
| GET | `/api/sport/sign/schedule?{id}` |  |  |  |
| GET | `/api/sport/sign/schedule/filters` |  |  | 200 |
| DELETE | `/api/sport/sign/schedule/lesson_groups/{id}` |  |  |  |
| POST | `/api/sport/sign/schedule/lesson_groups/{id}` |  |  |  |
| DELETE | `/api/sport/sign/schedule/lessons` |  |  |  |
| POST | `/api/sport/sign/schedule/lessons` |  |  |  |
| GET | `/api/sport/sign/schedule/lessons/{id}/other` |  |  |  |
| GET | `/api/sport/sign/schedule/limits` |  |  | 200 |
| GET | `/api/sport/sport_types` |  |  | 200 |
| GET | `/api/sport/time_slots` |  |  | 200 |

### system (student, 3)

MCP: itmo_student_info (dashboard), itmo_sitemap

| | Путь | Query | Риск | Статус |
|---|---|---|---|---|
| GET | `/api/system/dashboard` |  |  | 200 |
| GET | `/api/system/v1/menu/items` |  |  | 200 |
| GET | `/api/system/v1/menu/services` |  |  | 200 |

### vacation (staff, 25)

Служебный модуль, эндпоинты см. в `data/api-catalog.json`.
