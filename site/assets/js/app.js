/* Keiwijs Planner - front end. Vanilla ES2020, no dependencies.
 * The pasted Smartschool URL lives in memory only (never in localStorage/cookies). */
(() => {
  'use strict';

  // ------------------------------------------------------------------ config + i18n
  const API_BASE = (document.querySelector('meta[name="api-base"]')?.content || '').replace(/\/+$/, '');
  const LOCALE = document.documentElement.lang || 'nl-BE';
  let STRINGS = {};
  try {
    STRINGS = JSON.parse(document.getElementById('i18n')?.textContent || '{}');
  } catch {
    STRINGS = {};
  }

  /** Translate a key; `{name}` placeholders are replaced from vars. */
  const t = (key, vars = {}) =>
    (STRINGS[key] ?? key).replace(/\{(\w+)\}/g, (_, k) => (vars[k] ?? `{${k}}`));

  const LIMITS = {
    maxTags: 30, maxTagName: 40, maxKeywords: 20, maxKeywordLen: 60, maxIconRules: 30, maxIconKeyword: 40, maxIcon: 16,
  };
  const DEFAULT_MONTH_DAY = '08-01';
  // Mirrors DEFAULT_ICON_RULES / DEFAULT_FALLBACK_ICON in planner/ssfilter/icons.py.
  const DEFAULT_ICON_RULES = [
    ['vakantie', '☀\uFE0F'], ['geen school', '☀\uFE0F'], ['studiedag', '☀\uFE0F'], ['bib', '📚'], ['toets', '📝'],
    ['rapport', '📄'], ['oudercontact', '👥'], ['vaccin', '💉'], ['zeeklassen', '🌊'], ['bosklassen', '🌲'],
    ['schoolfeest', '🎉'], ['uitstap', '🚌'], ['zwemmen', '🏊'],
  ];
  const DEFAULT_FALLBACK_ICON = '📌';
  const DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  const SMARTSCHOOL_MARKER = '.smartschool.be/planner/sync/ics/';

  // ------------------------------------------------------------------ DOM helpers
  const $ = (id) => document.getElementById(id);
  const el = (tag, props = {}, ...children) => {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
      if (k === 'class') node.className = v;
      else if (k === 'text') node.textContent = v;
      else if (k in node && k !== 'list') node[k] = v;
      else node.setAttribute(k, v);
    }
    node.append(...children.filter((c) => c != null));
    return node;
  };
  const show = (node, visible) => { node.hidden = !visible; };

  const ui = {
    form: $('inspect-form'), url: $('url'), urlError: $('url-error'), btnInspect: $('btn-inspect'),
    status: $('status'), editor: $('editor'), banner: $('banner-existing'), calSummary: $('calendar-summary'),
    tagList: $('tag-list'), btnAddTag: $('btn-add-tag'),
    rollDay: $('roll-day'), rollMonth: $('roll-month'), nextRollover: $('next-rollover'),
    includeUntagged: $('include-untagged'), useOrganisator: $('use-organisator'), includeParticipants: $('include-participants'),
    titleIcons: $('title-icons'), iconRules: $('icon-rules'), iconList: $('icon-list'), btnAddIcon: $('btn-add-icon'),
    fallbackIcon: $('fallback-icon'),
    settingsError: $('settings-error'),
    previewCount: $('preview-count'), previewBody: $('preview-body'), onlyDropped: $('only-dropped'),
    btnGenerate: $('btn-generate'), btnDelete: $('btn-delete'),
    result: $('result'), resultMessage: $('result-message'), feedUrl: $('feed-url'), webcalUrl: $('webcal-url'),
    btnTest: $('btn-test'), testResult: $('test-result'),
  };

  // ------------------------------------------------------------------ state
  const defaultSettings = () => ({
    tags: [],
    includeUntagged: true,
    includeKeywords: [],
    excludeKeywords: [],
    useOrganisator: false,
    stripParticipants: true,
    titleIcons: true,
    iconRules: DEFAULT_ICON_RULES.map(([keyword, icon]) => ({ keyword, icon })),
    fallbackIcon: DEFAULT_FALLBACK_ICON,
    rolloverMonthDay: DEFAULT_MONTH_DAY,
  });

  /** Trim, and add VS16 to a lone text-presentation symbol so it renders full width (mirrors the server). */
  const normaliseIcon = (raw) => {
    const icon = String(raw ?? '').trim();
    const chars = Array.from(icon);
    if (chars.length === 1 && /\p{So}/u.test(icon) && icon.codePointAt(0) < 0x1F000) return `${icon}\uFE0F`;
    return icon;
  };
  const cleanKeyword = (raw) => String(raw ?? '').trim().replace(/\s+/g, ' ');

  const state = {
    url: '',                 // pasted Smartschool link (memory only)
    settings: defaultSettings(),
    tagHits: {},
    nextRolloverUtc: null,
    events: [],
    keptCount: 0,
    eventCount: 0,
    existing: false,
    feedUrl: '',
    busy: 0,
    previewSeq: 0,
    previewAbort: null,
  };

  // ------------------------------------------------------------------ API
  class ApiError extends Error {
    constructor(code, message, status) {
      super(message);
      this.code = code;
      this.status = status;
    }
  }

  async function api(method, path, body, signal) {
    let res;
    try {
      res = await fetch(`${API_BASE}${path}`, {
        method,
        headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal,
      });
    } catch (err) {
      if (err?.name === 'AbortError') throw err;
      throw new ApiError('network', String(err), 0);
    }
    let data = null;
    try {
      data = await res.json();
    } catch {
      data = null;
    }
    if (!res.ok) {
      throw new ApiError(data?.error || `http_${res.status}`, data?.message || res.statusText, res.status);
    }
    return data ?? {};
  }

  function friendlyError(err) {
    const code = err instanceof ApiError ? err.code : 'network';
    if (code === 'invalid_url') return t('err_invalid_url');
    if (code === 'invalid_settings') return t('err_invalid_settings');
    if (code === 'rate_limited') return t('err_rate_limited');
    if (code.startsWith('upstream_')) return t('err_upstream');
    if (code === 'network') return t('err_network');
    return t('err_internal');
  }

  // ------------------------------------------------------------------ busy / status
  function setBusy(on, message = '') {
    state.busy = Math.max(0, state.busy + (on ? 1 : -1));
    const busy = state.busy > 0;
    for (const b of [ui.btnInspect, ui.btnGenerate, ui.btnDelete, ui.btnTest]) b.disabled = busy;
    ui.status.textContent = busy ? (message || t('loading')) : '';
    document.body.setAttribute('aria-busy', String(busy));
  }

  const showError = (node, message) => {
    node.textContent = message || '';
    show(node, Boolean(message));
  };

  // ------------------------------------------------------------------ validation (mirrors the server)
  function validateUrl(raw) {
    const url = raw.trim();
    if (!url) return t('err_empty_url');
    if (!url.toLowerCase().startsWith('https://')) return t('err_https');
    if (!url.toLowerCase().includes(SMARTSCHOOL_MARKER)) return t('err_smartschool');
    return null;
  }

  /** Returns the first validation message for the current settings, or null. */
  function validateSettings(s) {
    if (s.tags.length < 1 || s.tags.length > LIMITS.maxTags) return t('err_tags_count');
    const seen = new Set();
    for (const tag of s.tags) {
      const name = tag.name.trim();
      if (!name) return t('err_tag_empty');
      if (name.length > LIMITS.maxTagName) return t('err_tag_long');
      const key = name.toLowerCase();
      if (seen.has(key)) return t('err_tag_dup', { name });
      seen.add(key);
    }
    for (const list of [s.includeKeywords, s.excludeKeywords]) {
      if (list.length > LIMITS.maxKeywords) return t('err_kw_count');
      if (list.some((w) => w.length > LIMITS.maxKeywordLen)) return t('err_kw_long');
    }
    if (s.iconRules.length > LIMITS.maxIconRules) return t('err_icon_count');
    const seenIcons = new Set();
    for (const rule of s.iconRules) {
      const keyword = cleanKeyword(rule.keyword);
      const icon = normaliseIcon(rule.icon);
      if (!keyword || !icon) return t('err_icon_empty');
      if (keyword.length > LIMITS.maxIconKeyword || icon.length > LIMITS.maxIcon) return t('err_icon_long');
      if (/\s/.test(icon)) return t('err_icon_space');
      const key = keyword.toLowerCase();
      if (seenIcons.has(key)) return t('err_icon_dup', { name: keyword });
      seenIcons.add(key);
    }
    const fallback = normaliseIcon(s.fallbackIcon);
    if (fallback.length > LIMITS.maxIcon) return t('err_icon_long');
    if (/\s/.test(fallback)) return t('err_icon_space');
    return null;
  }

  /** Exact payload shape expected by the API. */
  function buildSettings() {
    const s = state.settings;
    return {
      tags: s.tags.map((tag) => ({
        name: tag.name.trim(),
        selected: Boolean(tag.selected),
        moveNext: Boolean(tag.selected && tag.moveNext),
      })),
      includeUntagged: Boolean(s.includeUntagged),
      includeKeywords: [...s.includeKeywords],
      excludeKeywords: [...s.excludeKeywords],
      useOrganisator: Boolean(s.useOrganisator),
      stripParticipants: Boolean(s.stripParticipants),
      titleIcons: Boolean(s.titleIcons),
      iconRules: s.iconRules.map((r) => ({ keyword: cleanKeyword(r.keyword), icon: normaliseIcon(r.icon) })),
      fallbackIcon: normaliseIcon(s.fallbackIcon),
      rolloverMonthDay: s.rolloverMonthDay,
    };
  }

  /** Normalise settings coming from the server into editable state. */
  function adoptSettings(dto) {
    const base = defaultSettings();
    state.settings = {
      tags: (dto?.tags ?? []).map((x) => ({
        name: String(x.name ?? ''),
        selected: Boolean(x.selected),
        moveNext: Boolean(x.selected && x.moveNext),
      })),
      includeUntagged: dto?.includeUntagged ?? base.includeUntagged,
      includeKeywords: [...(dto?.includeKeywords ?? [])],
      excludeKeywords: [...(dto?.excludeKeywords ?? [])],
      useOrganisator: dto?.useOrganisator ?? base.useOrganisator,
      stripParticipants: dto?.stripParticipants ?? base.stripParticipants,
      titleIcons: dto?.titleIcons ?? base.titleIcons,
      iconRules: Array.isArray(dto?.iconRules)
        ? dto.iconRules.map((r) => ({ keyword: String(r.keyword ?? ''), icon: String(r.icon ?? '') }))
        : base.iconRules,
      fallbackIcon: typeof dto?.fallbackIcon === 'string' ? dto.fallbackIcon : base.fallbackIcon,
      rolloverMonthDay: /^\d{2}-\d{2}$/.test(dto?.rolloverMonthDay ?? '') ? dto.rolloverMonthDay : base.rolloverMonthDay,
    };
    state.nextRolloverUtc = dto?.nextRolloverUtc ?? null;
  }

  // ------------------------------------------------------------------ formatting
  const parseWhen = (value) => {
    if (!value) return null;
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
      const [y, m, d] = value.split('-').map(Number);
      return new Date(y, m - 1, d);
    }
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  };

  const fmtDate = new Intl.DateTimeFormat(LOCALE, { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
  const fmtDateTime = new Intl.DateTimeFormat(LOCALE, {
    weekday: 'short', day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
  });

  function formatWhen(start, allDay) {
    const date = parseWhen(start);
    if (!date) return start || '';
    return allDay ? fmtDate.format(date) : fmtDateTime.format(date);
  }

  // ------------------------------------------------------------------ tag editor
  function hitsFor(name) {
    const hits = state.tagHits;
    const key = Object.keys(hits).find((k) => k.toLowerCase() === name.trim().toLowerCase());
    return key === undefined ? null : hits[key];
  }

  function updateBadge(badge, name) {
    const hits = hitsFor(name);
    badge.textContent = hits === null ? '?' : String(hits);
    badge.classList.toggle('zero', !hits);
    badge.title = hits === null ? t('hits_unknown') : t('hits_title', { n: hits });
  }

  function renderTags(focus) {
    const tags = state.settings.tags;
    ui.tagList.replaceChildren(...tags.map((tag, i) => tagRow(tag, i, tags.length)));
    ui.btnAddTag.disabled = tags.length >= LIMITS.maxTags;
    if (focus) ui.tagList.querySelector(focus)?.focus();
  }

  const iconButton = (text, label, subject, action, disabled = false) =>
    el('button', { type: 'button', class: 'btn btn-icon', 'aria-label': `${label} ${subject}`.trim(), title: label, text, disabled, 'data-action': action });

  /** Inline SVG cloned from a <template> in list.html. */
  const svgIcon = (id) => $(id)?.content.firstElementChild?.cloneNode(true) ?? null;

  /** Checkbox whose visible label is an icon; the text lives in aria-label and a tooltip. */
  const iconCheck = (input, iconId, tip) =>
    el('label', { class: 'check icon-check tip', 'data-tip': tip }, input, svgIcon(iconId));

  /** Move list[from] to list[to] (neighbours) and re-render with focus on the same control. */
  function swapRows(list, from, to, action, rerender) {
    [list[from], list[to]] = [list[to], list[from]];
    rerender(`li:nth-child(${to + 1}) [data-action="${action}"]:not(:disabled)`);
    changed();
  }

  function tagRow(tag, index, total) {
    const data = ui.tagList.dataset;
    const iconBtn = (text, label, action, disabled = false) => iconButton(text, label, tag.name, action, disabled);

    const name = el('input', {
      type: 'text', class: 'tag-name', value: tag.name, maxLength: 80,
      placeholder: t('new_tag_placeholder'), 'aria-label': data.nameLabel, autocomplete: 'off',
    });
    const badge = el('span', { class: 'badge' });
    updateBadge(badge, tag.name);

    const selected = el('input', { type: 'checkbox', checked: tag.selected, 'aria-label': `${data.selected} ${tag.name}`.trim() });
    const move = el('input', {
      type: 'checkbox', checked: tag.selected && tag.moveNext, disabled: !tag.selected, 'aria-label': `${data.move} ${tag.name}`.trim(),
    });

    name.addEventListener('input', () => {
      tag.name = name.value;
      updateBadge(badge, tag.name);
      selected.setAttribute('aria-label', `${data.selected} ${tag.name}`.trim());
      move.setAttribute('aria-label', `${data.move} ${tag.name}`.trim());
      changed();
    });
    selected.addEventListener('change', () => {
      tag.selected = selected.checked;
      tag.moveNext = selected.checked;
      move.checked = tag.moveNext;
      move.disabled = !tag.selected;
      changed();
    });
    move.addEventListener('change', () => {
      tag.moveNext = move.checked;
      changed();
    });

    const swap = (to, action) => swapRows(state.settings.tags, index, to, action, renderTags);
    const up = iconBtn('↑', data.up, 'up', index === 0);
    const down = iconBtn('↓', data.down, 'down', index === total - 1);
    const del = iconBtn('×', data.del, 'del');
    up.addEventListener('click', () => swap(index - 1, 'up'));
    down.addEventListener('click', () => swap(index + 1, 'down'));
    del.addEventListener('click', () => {
      state.settings.tags.splice(index, 1);
      renderTags(state.settings.tags.length ? `li:nth-child(${Math.min(index + 1, state.settings.tags.length)}) .tag-name` : null);
      changed();
    });

    return el('li', { class: 'tag-row' },
      el('span', { class: 'tag-order' }, up, down),
      name,
      iconCheck(selected, 'icon-include', data.selectedTip),
      iconCheck(move, 'icon-move', data.moveTip),
      badge,
      el('span', { class: 'spacer' }),
      del);
  }

  // ------------------------------------------------------------------ title icon rules
  function renderIconRules(focus) {
    const rules = state.settings.iconRules;
    ui.iconList.replaceChildren(...rules.map((rule, i) => iconRuleRow(rule, i, rules.length)));
    ui.btnAddIcon.disabled = rules.length >= LIMITS.maxIconRules;
    if (focus) ui.iconList.querySelector(focus)?.focus();
  }

  function iconRuleRow(rule, index, total) {
    const data = ui.iconList.dataset;
    const iconBtn = (text, label, action, disabled = false) => iconButton(text, label, rule.keyword, action, disabled);
    const keyword = el('input', {
      type: 'text', class: 'icon-keyword', value: rule.keyword, maxLength: LIMITS.maxIconKeyword,
      'aria-label': data.keywordLabel, autocomplete: 'off',
    });
    const icon = el('input', {
      type: 'text', class: 'icon-input', value: rule.icon, maxLength: LIMITS.maxIcon, 'aria-label': data.iconLabel, autocomplete: 'off',
    });
    keyword.addEventListener('input', () => { rule.keyword = keyword.value; changed(); });
    icon.addEventListener('input', () => { rule.icon = icon.value; changed(); });
    icon.addEventListener('blur', () => { icon.value = rule.icon = normaliseIcon(icon.value); });

    const swap = (to, action) => swapRows(state.settings.iconRules, index, to, action, renderIconRules);
    const up = iconBtn('↑', data.up, 'up', index === 0);
    const down = iconBtn('↓', data.down, 'down', index === total - 1);
    const del = iconBtn('×', data.del, 'del');
    up.addEventListener('click', () => swap(index - 1, 'up'));
    down.addEventListener('click', () => swap(index + 1, 'down'));
    del.addEventListener('click', () => {
      state.settings.iconRules.splice(index, 1);
      const left = state.settings.iconRules.length;
      renderIconRules(left ? `li:nth-child(${Math.min(index + 1, left)}) .icon-keyword` : null);
      changed();
    });

    return el('li', { class: 'tag-row icon-row' }, el('span', { class: 'tag-order' }, up, down), keyword, icon, el('span', { class: 'spacer' }), del);
  }

  function renderIconSettings() {
    const s = state.settings;
    ui.titleIcons.checked = s.titleIcons;
    ui.iconRules.disabled = !s.titleIcons;
    ui.fallbackIcon.value = s.fallbackIcon;
    renderIconRules();
  }

  // ------------------------------------------------------------------ rollover date
  function initRolloverSelects() {
    const months = t('months').split(',');
    ui.rollMonth.replaceChildren(...months.map((name, i) => el('option', { value: String(i + 1), text: name })));
    fillDays(1);
    const sync = () => {
      const month = Number(ui.rollMonth.value);
      fillDays(month, Number(ui.rollDay.value));
      state.settings.rolloverMonthDay = `${String(month).padStart(2, '0')}-${String(ui.rollDay.value).padStart(2, '0')}`;
      changed();
    };
    ui.rollMonth.addEventListener('change', sync);
    ui.rollDay.addEventListener('change', sync);
  }

  function fillDays(month, keep = 1) {
    const max = DAYS_IN_MONTH[month - 1] ?? 31;
    const options = Array.from({ length: max }, (_, i) => el('option', { value: String(i + 1), text: String(i + 1) }));
    ui.rollDay.replaceChildren(...options);
    ui.rollDay.value = String(Math.min(keep, max));
  }

  function renderRollover() {
    const [mm, dd] = state.settings.rolloverMonthDay.split('-').map(Number);
    ui.rollMonth.value = String(mm);
    fillDays(mm, dd);
    const next = parseWhen(state.nextRolloverUtc);
    ui.nextRollover.textContent = next
      ? t('next_rollover', { date: new Intl.DateTimeFormat(LOCALE, { day: 'numeric', month: 'long', year: 'numeric' }).format(next) })
      : '';
  }

  // ------------------------------------------------------------------ chip inputs
  function chipInput(container, listKey) {
    const input = container.querySelector('input');
    const render = () => {
      container.querySelectorAll('.chip').forEach((c) => c.remove());
      for (const word of state.settings[listKey]) {
        const remove = el('button', { type: 'button', 'aria-label': t('chip_remove', { word }), text: '×' });
        remove.addEventListener('click', () => {
          state.settings[listKey] = state.settings[listKey].filter((w) => w !== word);
          render();
          changed();
          input.focus();
        });
        container.insertBefore(el('span', { class: 'chip' }, word, remove), input);
      }
    };
    const commit = () => {
      const words = input.value.split(',').map((w) => w.trim().replace(/\s+/g, ' ')).filter(Boolean);
      input.value = '';
      const list = state.settings[listKey];
      for (const w of words) {
        if (!list.some((x) => x.toLowerCase() === w.toLowerCase())) list.push(w);
      }
      render();
      if (words.length) changed();
    };
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ',') {
        e.preventDefault();
        commit();
      } else if (e.key === 'Backspace' && !input.value && state.settings[listKey].length) {
        state.settings[listKey].pop();
        render();
        changed();
      }
    });
    input.addEventListener('blur', commit);
    return render;
  }

  let renderIncludeChips = () => {};
  let renderExcludeChips = () => {};

  // ------------------------------------------------------------------ preview
  let previewTimer = 0;
  const schedulePreview = () => {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(refreshPreview, 400);
  };

  /** Called after any settings edit. */
  function changed() {
    const problem = validateSettings(state.settings);
    showError(ui.settingsError, problem);
    ui.btnGenerate.disabled = state.busy > 0;
    schedulePreview();
  }

  async function refreshPreview() {
    if (!state.url) return;
    if (validateSettings(state.settings)) return;
    state.previewAbort?.abort();
    const abort = new AbortController();
    state.previewAbort = abort;
    const seq = ++state.previewSeq;
    ui.previewCount.textContent = t('preview_loading');
    try {
      const data = await api('POST', '/api/preview', { url: state.url, settings: buildSettings() }, abort.signal);
      if (seq !== state.previewSeq) return;
      applyPreview(data);
      showError(ui.settingsError, '');
    } catch (err) {
      if (err?.name === 'AbortError' || seq !== state.previewSeq) return;
      ui.previewCount.textContent = '';
      showError(ui.settingsError, friendlyError(err));
    }
  }

  function applyPreview(data) {
    state.events = data.events ?? [];
    state.eventCount = data.eventCount ?? state.events.length;
    state.keptCount = data.keptCount ?? state.events.filter((e) => e.keep).length;
    if (data.tagHits) {
      state.tagHits = data.tagHits;
      document.querySelectorAll('.tag-row').forEach((row, i) => {
        const tag = state.settings.tags[i];
        if (tag) updateBadge(row.querySelector('.badge'), tag.name);
      });
    }
    if (data.calendarName !== undefined) renderCalendarSummary(data.calendarName);
    renderPreview();
  }

  function renderCalendarSummary(name) {
    ui.calSummary.textContent = t('calendar_summary', { name: name || t('calendar_unnamed'), count: state.eventCount });
  }

  function reasonText(reason, detail) {
    const key = `reason_${reason}`;
    return STRINGS[key] ? t(key, { detail: detail ?? '' }) : String(reason ?? '');
  }

  function renderPreview() {
    ui.previewCount.textContent = t('preview_count', { kept: state.keptCount, total: state.eventCount });
    const onlyDropped = ui.onlyDropped.checked;
    const rows = state.events.filter((e) => !onlyDropped || !e.keep);
    if (!rows.length) {
      const cell = el('td', { colSpan: 4, text: t('preview_empty') });
      ui.previewBody.replaceChildren(el('tr', {}, cell));
      return;
    }
    ui.previewBody.replaceChildren(...rows.map((e) => {
      const status = e.keep
        ? el('td', {}, el('span', { class: 'dot', 'aria-hidden': 'true' }), t('status_kept'), el('span', { class: 'help', text: ` ${reasonText(e.reason, e.detail)}` }))
        : el('td', { text: `${t('status_dropped')}: ${reasonText(e.reason, e.detail)}` });
      return el('tr', { class: e.keep ? 'kept' : 'dropped' },
        el('td', { class: 'when', text: formatWhen(e.start, e.allDay) }),
        el('td', { class: 'summary', text: e.icon ? `${e.icon} ${e.summary || ''}` : (e.summary || '') }),
        el('td', {}, ...(e.tags ?? []).map((name) => el('span', { class: 'tag-chip', text: name }))),
        status);
    }));
  }

  // ------------------------------------------------------------------ editor rendering
  function renderEditor() {
    const s = state.settings;
    ui.includeUntagged.checked = s.includeUntagged;
    ui.useOrganisator.checked = s.useOrganisator;
    ui.includeParticipants.checked = !s.stripParticipants;
    renderTags();
    renderIconSettings();
    renderRollover();
    renderIncludeChips();
    renderExcludeChips();
    show(ui.banner, state.existing);
    ui.banner.textContent = state.existing ? t('existing_banner') : '';
    ui.btnGenerate.textContent = t(state.existing ? 'btn_save' : 'btn_generate');
    show(ui.btnDelete, state.existing);
    showError(ui.settingsError, validateSettings(s));
  }

  // Shows the (never-changing) feed links, or hides the block when `data` is null.
  function renderResult(data, message = '') {
    ui.feedUrl.value = data?.feedUrl || '';
    ui.webcalUrl.value = data?.webcalUrl || '';
    ui.resultMessage.textContent = message;
    show(ui.resultMessage, Boolean(message));
    show(ui.result, Boolean(data));
    ui.testResult.textContent = '';
  }

  function resetAll() {
    clearTimeout(previewTimer);
    state.previewAbort?.abort();
    state.previewSeq += 1;
    Object.assign(state, {
      url: '', settings: defaultSettings(), tagHits: {}, nextRolloverUtc: null, events: [],
      keptCount: 0, eventCount: 0, existing: false, feedUrl: '',
    });
    ui.url.value = '';
    show(ui.editor, false);
    renderResult(null);
    ui.previewBody.replaceChildren();
    ui.previewCount.textContent = '';
    ui.url.focus();
  }

  // ------------------------------------------------------------------ actions
  async function onInspect(event) {
    event.preventDefault();
    const raw = ui.url.value;
    const problem = validateUrl(raw);
    showError(ui.urlError, problem);
    if (problem) return;
    setBusy(true);
    try {
      const data = await api('POST', '/api/inspect', { url: raw.trim() });
      state.url = raw.trim();
      state.existing = data.existing === true;
      state.tagHits = data.tagHits ?? {};
      state.feedUrl = data.feedUrl ?? '';
      adoptSettings(data.settings);
      state.events = data.events ?? [];
      state.eventCount = data.eventCount ?? state.events.length;
      state.keptCount = data.keptCount ?? 0;
      renderResult(state.existing ? data : null);
      show(ui.editor, true);
      renderEditor();
      renderCalendarSummary(data.calendarName);
      renderPreview();
    } catch (err) {
      showError(ui.urlError, friendlyError(err));
    } finally {
      setBusy(false);
    }
  }

  async function onGenerate() {
    const problem = validateSettings(state.settings);
    showError(ui.settingsError, problem);
    if (problem) return;
    setBusy(true);
    try {
      const data = await api('POST', '/api/config', { url: state.url, settings: buildSettings() });
      state.existing = true;
      state.feedUrl = data.feedUrl;
      if (data.settings) {
        state.nextRolloverUtc = data.settings.nextRolloverUtc ?? state.nextRolloverUtc;
        renderRollover();
      }
      const messages = [data.created ? t('saved_new') : t('saved_update')];
      const render = data.render ?? {};
      if (render.ok === false) messages.push(t('render_warning', { error: render.error || '?' }));
      if (render.rollovers?.some((r) => r && r !== 'geen wijzigingen')) {
        messages.push(t('rollovers_applied', { summary: render.rollovers.join('; ') }));
      }
      renderResult(data, messages.join(' '));
      ui.btnGenerate.textContent = t('btn_save');
      show(ui.btnDelete, true);
      ui.result.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (err) {
      showError(ui.settingsError, friendlyError(err));
    } finally {
      setBusy(false);
    }
  }

  async function onDelete() {
    if (!window.confirm(t('delete_confirm'))) return;
    setBusy(true);
    try {
      await api('DELETE', '/api/config', { url: state.url });
      resetAll();
      ui.status.textContent = t('deleted');
    } catch (err) {
      showError(ui.settingsError, friendlyError(err));
    } finally {
      setBusy(false);
      if (!state.url) ui.status.textContent = t('deleted');
    }
  }

  async function onTest() {
    if (!state.feedUrl) return;
    setBusy(true);
    ui.testResult.textContent = '';
    try {
      const res = await fetch(state.feedUrl, { cache: 'no-store' });
      if (!res.ok) throw new Error(`http ${res.status}`);
      const text = await res.text();
      const count = (text.match(/BEGIN:VEVENT/g) || []).length;
      const name = /^X-WR-CALNAME[^:]*:(.*)$/m.exec(text)?.[1]?.trim() || t('calendar_unnamed');
      ui.testResult.textContent = t('test_result', { count, name });
    } catch {
      // Most likely CORS on the feed host: fall back to opening it in a new tab.
      window.open(state.feedUrl, '_blank', 'noopener');
      ui.testResult.textContent = t('test_opened');
    } finally {
      setBusy(false);
    }
  }

  async function onCopy(button) {
    const input = $(button.dataset.copy);
    const original = button.textContent;
    try {
      await navigator.clipboard.writeText(input.value);
    } catch {
      input.select();
      document.execCommand?.('copy');
    }
    button.textContent = t('copied');
    setTimeout(() => { button.textContent = original; }, 1800);
  }

  // ------------------------------------------------------------------ init
  function init() {
    if (!ui.form) return;
    initRolloverSelects();
    renderIncludeChips = chipInput($('include-kw-chips'), 'includeKeywords');
    renderExcludeChips = chipInput($('exclude-kw-chips'), 'excludeKeywords');

    ui.form.addEventListener('submit', onInspect);
    ui.url.addEventListener('input', () => showError(ui.urlError, ''));
    ui.btnAddTag.addEventListener('click', () => {
      state.settings.tags.push({ name: '', selected: false, moveNext: false });
      renderTags('li:last-child .tag-name');
      changed();
    });
    ui.includeUntagged.addEventListener('change', () => { state.settings.includeUntagged = ui.includeUntagged.checked; changed(); });
    ui.useOrganisator.addEventListener('change', () => { state.settings.useOrganisator = ui.useOrganisator.checked; changed(); });
    ui.includeParticipants.addEventListener('change', () => { state.settings.stripParticipants = !ui.includeParticipants.checked; changed(); });
    ui.titleIcons.addEventListener('change', () => {
      state.settings.titleIcons = ui.titleIcons.checked;
      ui.iconRules.disabled = !ui.titleIcons.checked;
      changed();
    });
    ui.btnAddIcon.addEventListener('click', () => {
      state.settings.iconRules.push({ keyword: '', icon: '' });
      renderIconRules('li:last-child .icon-keyword');
      changed();
    });
    ui.fallbackIcon.addEventListener('input', () => { state.settings.fallbackIcon = ui.fallbackIcon.value; changed(); });
    ui.fallbackIcon.addEventListener('blur', () => {
      ui.fallbackIcon.value = state.settings.fallbackIcon = normaliseIcon(ui.fallbackIcon.value);
    });
    ui.onlyDropped.addEventListener('change', renderPreview);
    ui.btnGenerate.addEventListener('click', onGenerate);
    ui.btnDelete.addEventListener('click', onDelete);
    ui.btnTest.addEventListener('click', onTest);
    document.querySelectorAll('[data-copy]').forEach((b) => b.addEventListener('click', () => onCopy(b)));
    for (const input of [ui.feedUrl, ui.webcalUrl]) input.addEventListener('focus', () => input.select());
  }

  init();
})();
