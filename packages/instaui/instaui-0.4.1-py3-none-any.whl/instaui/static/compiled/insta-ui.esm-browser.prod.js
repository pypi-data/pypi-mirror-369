var Nr = Object.defineProperty;
var Or = (e, t, n) => t in e ? Nr(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var H = (e, t, n) => Or(e, typeof t != "symbol" ? t + "" : t, n);
import * as kr from "vue";
import { unref as U, onMounted as mn, nextTick as Se, ref as G, readonly as Rt, getCurrentInstance as Ue, toRef as pe, customRef as fe, watch as q, isRef as Pt, getCurrentScope as xr, onScopeDispose as Ar, shallowRef as Q, watchEffect as Ct, computed as I, toRaw as vn, toValue as $e, provide as be, inject as te, shallowReactive as $r, defineComponent as j, reactive as Ir, h as D, onUnmounted as Tr, renderList as Dr, TransitionGroup as yn, cloneVNode as ae, withDirectives as wn, withModifiers as Mr, normalizeStyle as jr, normalizeClass as at, toDisplayString as _n, vModelDynamic as Lr, vShow as Wr, resolveDynamicComponent as Fr, normalizeProps as Br, onErrorCaptured as Hr, openBlock as ie, createElementBlock as ge, createElementVNode as En, createVNode as zr, createCommentVNode as ct, createTextVNode as Ur, createBlock as bn, Teleport as Gr, renderSlot as Sn, useAttrs as Kr, Fragment as Vn, mergeProps as qr, KeepAlive as Jr } from "vue";
let Rn;
function Qr(e) {
  Rn = e;
}
function lt() {
  return Rn;
}
function Be() {
  const { queryPath: e, pathParams: t, queryParams: n } = lt();
  return {
    path: e,
    ...t === void 0 ? {} : { params: t },
    ...n === void 0 ? {} : { queryParams: n }
  };
}
const Nt = /* @__PURE__ */ new Map();
function Yr(e) {
  var t;
  (t = e.scopes) == null || t.forEach((n) => {
    Nt.set(n.id, n);
  });
}
function tt(e) {
  return Nt.get(e);
}
function Ce(e) {
  return e && Nt.has(e);
}
function Pn(e) {
  return xr() ? (Ar(e), !0) : !1;
}
function se(e) {
  return typeof e == "function" ? e() : U(e);
}
const Xr = typeof window < "u" && typeof document < "u";
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const Zr = Object.prototype.toString, eo = (e) => Zr.call(e) === "[object Object]", Ie = () => {
};
function to(e, t) {
  function n(...r) {
    return new Promise((o, s) => {
      Promise.resolve(e(() => t.apply(this, r), { fn: t, thisArg: this, args: r })).then(o).catch(s);
    });
  }
  return n;
}
const Cn = (e) => e();
function no(e = Cn) {
  const t = G(!0);
  function n() {
    t.value = !1;
  }
  function r() {
    t.value = !0;
  }
  const o = (...s) => {
    t.value && e(...s);
  };
  return { isActive: Rt(t), pause: n, resume: r, eventFilter: o };
}
function ut(e, t = !1, n = "Timeout") {
  return new Promise((r, o) => {
    setTimeout(t ? () => o(n) : r, e);
  });
}
function ro(e) {
  return Ue();
}
function oo(...e) {
  if (e.length !== 1)
    return pe(...e);
  const t = e[0];
  return typeof t == "function" ? Rt(fe(() => ({ get: t, set: Ie }))) : G(t);
}
function so(e, t, n = {}) {
  const {
    eventFilter: r = Cn,
    ...o
  } = n;
  return q(
    e,
    to(
      r,
      t
    ),
    o
  );
}
function io(e, t, n = {}) {
  const {
    eventFilter: r,
    ...o
  } = n, { eventFilter: s, pause: i, resume: c, isActive: u } = no(r);
  return { stop: so(
    e,
    t,
    {
      ...o,
      eventFilter: s
    }
  ), pause: i, resume: c, isActive: u };
}
function Nn(e, t = !0, n) {
  ro() ? mn(e, n) : t ? e() : Se(e);
}
function ft(e, t = !1) {
  function n(a, { flush: f = "sync", deep: h = !1, timeout: g, throwOnTimeout: m } = {}) {
    let v = null;
    const w = [new Promise((b) => {
      v = q(
        e,
        (V) => {
          a(V) !== t && (v ? v() : Se(() => v == null ? void 0 : v()), b(V));
        },
        {
          flush: f,
          deep: h,
          immediate: !0
        }
      );
    })];
    return g != null && w.push(
      ut(g, m).then(() => se(e)).finally(() => v == null ? void 0 : v())
    ), Promise.race(w);
  }
  function r(a, f) {
    if (!Pt(a))
      return n((V) => V === a, f);
    const { flush: h = "sync", deep: g = !1, timeout: m, throwOnTimeout: v } = f ?? {};
    let y = null;
    const b = [new Promise((V) => {
      y = q(
        [e, a],
        ([A, F]) => {
          t !== (A === F) && (y ? y() : Se(() => y == null ? void 0 : y()), V(A));
        },
        {
          flush: h,
          deep: g,
          immediate: !0
        }
      );
    })];
    return m != null && b.push(
      ut(m, v).then(() => se(e)).finally(() => (y == null || y(), se(e)))
    ), Promise.race(b);
  }
  function o(a) {
    return n((f) => !!f, a);
  }
  function s(a) {
    return r(null, a);
  }
  function i(a) {
    return r(void 0, a);
  }
  function c(a) {
    return n(Number.isNaN, a);
  }
  function u(a, f) {
    return n((h) => {
      const g = Array.from(h);
      return g.includes(a) || g.includes(se(a));
    }, f);
  }
  function d(a) {
    return l(1, a);
  }
  function l(a = 1, f) {
    let h = -1;
    return n(() => (h += 1, h >= a), f);
  }
  return Array.isArray(se(e)) ? {
    toMatch: n,
    toContains: u,
    changed: d,
    changedTimes: l,
    get not() {
      return ft(e, !t);
    }
  } : {
    toMatch: n,
    toBe: r,
    toBeTruthy: o,
    toBeNull: s,
    toBeNaN: c,
    toBeUndefined: i,
    changed: d,
    changedTimes: l,
    get not() {
      return ft(e, !t);
    }
  };
}
function ao(e) {
  return ft(e);
}
function co(e, t, n) {
  let r;
  Pt(n) ? r = {
    evaluating: n
  } : r = n || {};
  const {
    lazy: o = !1,
    evaluating: s = void 0,
    shallow: i = !0,
    onError: c = Ie
  } = r, u = G(!o), d = i ? Q(t) : G(t);
  let l = 0;
  return Ct(async (a) => {
    if (!u.value)
      return;
    l++;
    const f = l;
    let h = !1;
    s && Promise.resolve().then(() => {
      s.value = !0;
    });
    try {
      const g = await e((m) => {
        a(() => {
          s && (s.value = !1), h || m();
        });
      });
      f === l && (d.value = g);
    } catch (g) {
      c(g);
    } finally {
      s && f === l && (s.value = !1), h = !0;
    }
  }), o ? I(() => (u.value = !0, d.value)) : d;
}
const Te = Xr ? window : void 0;
function On(e) {
  var t;
  const n = se(e);
  return (t = n == null ? void 0 : n.$el) != null ? t : n;
}
function Wt(...e) {
  let t, n, r, o;
  if (typeof e[0] == "string" || Array.isArray(e[0]) ? ([n, r, o] = e, t = Te) : [t, n, r, o] = e, !t)
    return Ie;
  Array.isArray(n) || (n = [n]), Array.isArray(r) || (r = [r]);
  const s = [], i = () => {
    s.forEach((l) => l()), s.length = 0;
  }, c = (l, a, f, h) => (l.addEventListener(a, f, h), () => l.removeEventListener(a, f, h)), u = q(
    () => [On(t), se(o)],
    ([l, a]) => {
      if (i(), !l)
        return;
      const f = eo(a) ? { ...a } : a;
      s.push(
        ...n.flatMap((h) => r.map((g) => c(l, h, g, f)))
      );
    },
    { immediate: !0, flush: "post" }
  ), d = () => {
    u(), i();
  };
  return Pn(d), d;
}
function lo() {
  const e = G(!1), t = Ue();
  return t && mn(() => {
    e.value = !0;
  }, t), e;
}
function uo(e) {
  const t = lo();
  return I(() => (t.value, !!e()));
}
function fo(e, t, n) {
  const {
    immediate: r = !0,
    delay: o = 0,
    onError: s = Ie,
    onSuccess: i = Ie,
    resetOnExecute: c = !0,
    shallow: u = !0,
    throwError: d
  } = {}, l = u ? Q(t) : G(t), a = G(!1), f = G(!1), h = Q(void 0);
  async function g(y = 0, ...w) {
    c && (l.value = t), h.value = void 0, a.value = !1, f.value = !0, y > 0 && await ut(y);
    const b = typeof e == "function" ? e(...w) : e;
    try {
      const V = await b;
      l.value = V, a.value = !0, i(V);
    } catch (V) {
      if (h.value = V, s(V), d)
        throw V;
    } finally {
      f.value = !1;
    }
    return l.value;
  }
  r && g(o);
  const m = {
    state: l,
    isReady: a,
    isLoading: f,
    error: h,
    execute: g
  };
  function v() {
    return new Promise((y, w) => {
      ao(f).toBe(!1).then(() => y(m)).catch(w);
    });
  }
  return {
    ...m,
    then(y, w) {
      return v().then(y, w);
    }
  };
}
function ho(e, t = {}) {
  const { window: n = Te } = t, r = uo(() => n && "matchMedia" in n && typeof n.matchMedia == "function");
  let o;
  const s = G(!1), i = (d) => {
    s.value = d.matches;
  }, c = () => {
    o && ("removeEventListener" in o ? o.removeEventListener("change", i) : o.removeListener(i));
  }, u = Ct(() => {
    r.value && (c(), o = n.matchMedia(se(e)), "addEventListener" in o ? o.addEventListener("change", i) : o.addListener(i), s.value = o.matches);
  });
  return Pn(() => {
    u(), c(), o = void 0;
  }), s;
}
const Le = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {}, We = "__vueuse_ssr_handlers__", po = /* @__PURE__ */ go();
function go() {
  return We in Le || (Le[We] = Le[We] || {}), Le[We];
}
function kn(e, t) {
  return po[e] || t;
}
function mo(e) {
  return ho("(prefers-color-scheme: dark)", e);
}
function vo(e) {
  return e == null ? "any" : e instanceof Set ? "set" : e instanceof Map ? "map" : e instanceof Date ? "date" : typeof e == "boolean" ? "boolean" : typeof e == "string" ? "string" : typeof e == "object" ? "object" : Number.isNaN(e) ? "any" : "number";
}
const yo = {
  boolean: {
    read: (e) => e === "true",
    write: (e) => String(e)
  },
  object: {
    read: (e) => JSON.parse(e),
    write: (e) => JSON.stringify(e)
  },
  number: {
    read: (e) => Number.parseFloat(e),
    write: (e) => String(e)
  },
  any: {
    read: (e) => e,
    write: (e) => String(e)
  },
  string: {
    read: (e) => e,
    write: (e) => String(e)
  },
  map: {
    read: (e) => new Map(JSON.parse(e)),
    write: (e) => JSON.stringify(Array.from(e.entries()))
  },
  set: {
    read: (e) => new Set(JSON.parse(e)),
    write: (e) => JSON.stringify(Array.from(e))
  },
  date: {
    read: (e) => new Date(e),
    write: (e) => e.toISOString()
  }
}, Ft = "vueuse-storage";
function dt(e, t, n, r = {}) {
  var o;
  const {
    flush: s = "pre",
    deep: i = !0,
    listenToStorageChanges: c = !0,
    writeDefaults: u = !0,
    mergeDefaults: d = !1,
    shallow: l,
    window: a = Te,
    eventFilter: f,
    onError: h = (N) => {
      console.error(N);
    },
    initOnMounted: g
  } = r, m = (l ? Q : G)(typeof t == "function" ? t() : t);
  if (!n)
    try {
      n = kn("getDefaultStorage", () => {
        var N;
        return (N = Te) == null ? void 0 : N.localStorage;
      })();
    } catch (N) {
      h(N);
    }
  if (!n)
    return m;
  const v = se(t), y = vo(v), w = (o = r.serializer) != null ? o : yo[y], { pause: b, resume: V } = io(
    m,
    () => F(m.value),
    { flush: s, deep: i, eventFilter: f }
  );
  a && c && Nn(() => {
    n instanceof Storage ? Wt(a, "storage", Z) : Wt(a, Ft, ne), g && Z();
  }), g || Z();
  function A(N, $) {
    if (a) {
      const L = {
        key: e,
        oldValue: N,
        newValue: $,
        storageArea: n
      };
      a.dispatchEvent(n instanceof Storage ? new StorageEvent("storage", L) : new CustomEvent(Ft, {
        detail: L
      }));
    }
  }
  function F(N) {
    try {
      const $ = n.getItem(e);
      if (N == null)
        A($, null), n.removeItem(e);
      else {
        const L = w.write(N);
        $ !== L && (n.setItem(e, L), A($, L));
      }
    } catch ($) {
      h($);
    }
  }
  function B(N) {
    const $ = N ? N.newValue : n.getItem(e);
    if ($ == null)
      return u && v != null && n.setItem(e, w.write(v)), v;
    if (!N && d) {
      const L = w.read($);
      return typeof d == "function" ? d(L, v) : y === "object" && !Array.isArray(L) ? { ...v, ...L } : L;
    } else return typeof $ != "string" ? $ : w.read($);
  }
  function Z(N) {
    if (!(N && N.storageArea !== n)) {
      if (N && N.key == null) {
        m.value = v;
        return;
      }
      if (!(N && N.key !== e)) {
        b();
        try {
          (N == null ? void 0 : N.newValue) !== w.write(m.value) && (m.value = B(N));
        } catch ($) {
          h($);
        } finally {
          N ? Se(V) : V();
        }
      }
    }
  }
  function ne(N) {
    Z(N.detail);
  }
  return m;
}
const wo = "*,*::before,*::after{-webkit-transition:none!important;-moz-transition:none!important;-o-transition:none!important;-ms-transition:none!important;transition:none!important}";
function _o(e = {}) {
  const {
    selector: t = "html",
    attribute: n = "class",
    initialValue: r = "auto",
    window: o = Te,
    storage: s,
    storageKey: i = "vueuse-color-scheme",
    listenToStorageChanges: c = !0,
    storageRef: u,
    emitAuto: d,
    disableTransition: l = !0
  } = e, a = {
    auto: "",
    light: "light",
    dark: "dark",
    ...e.modes || {}
  }, f = mo({ window: o }), h = I(() => f.value ? "dark" : "light"), g = u || (i == null ? oo(r) : dt(i, r, s, { window: o, listenToStorageChanges: c })), m = I(() => g.value === "auto" ? h.value : g.value), v = kn(
    "updateHTMLAttrs",
    (V, A, F) => {
      const B = typeof V == "string" ? o == null ? void 0 : o.document.querySelector(V) : On(V);
      if (!B)
        return;
      const Z = /* @__PURE__ */ new Set(), ne = /* @__PURE__ */ new Set();
      let N = null;
      if (A === "class") {
        const L = F.split(/\s/g);
        Object.values(a).flatMap((Y) => (Y || "").split(/\s/g)).filter(Boolean).forEach((Y) => {
          L.includes(Y) ? Z.add(Y) : ne.add(Y);
        });
      } else
        N = { key: A, value: F };
      if (Z.size === 0 && ne.size === 0 && N === null)
        return;
      let $;
      l && ($ = o.document.createElement("style"), $.appendChild(document.createTextNode(wo)), o.document.head.appendChild($));
      for (const L of Z)
        B.classList.add(L);
      for (const L of ne)
        B.classList.remove(L);
      N && B.setAttribute(N.key, N.value), l && (o.getComputedStyle($).opacity, document.head.removeChild($));
    }
  );
  function y(V) {
    var A;
    v(t, n, (A = a[V]) != null ? A : V);
  }
  function w(V) {
    e.onChanged ? e.onChanged(V, y) : y(V);
  }
  q(m, w, { flush: "post", immediate: !0 }), Nn(() => w(m.value));
  const b = I({
    get() {
      return d ? g.value : m.value;
    },
    set(V) {
      g.value = V;
    }
  });
  return Object.assign(b, { store: g, system: h, state: m });
}
function Eo(e = {}) {
  const {
    valueDark: t = "dark",
    valueLight: n = ""
  } = e, r = _o({
    ...e,
    onChanged: (i, c) => {
      var u;
      e.onChanged ? (u = e.onChanged) == null || u.call(e, i === "dark", c, i) : c(i);
    },
    modes: {
      dark: t,
      light: n
    }
  }), o = I(() => r.system.value);
  return I({
    get() {
      return r.value === "dark";
    },
    set(i) {
      const c = i ? "dark" : "light";
      o.value === c ? r.value = "auto" : r.value = c;
    }
  });
}
function K(e, t) {
  t = t || {};
  const n = [...Object.keys(t), "__Vue"], r = [...Object.values(t), kr];
  try {
    return new Function(...n, `return (${e})`)(...r);
  } catch (o) {
    throw new Error(o + " in function code: " + e);
  }
}
function bo(e) {
  if (e.startsWith(":")) {
    e = e.slice(1);
    try {
      return K(e);
    } catch (t) {
      throw new Error(t + " in function code: " + e);
    }
  }
}
function xn(e) {
  return e.constructor.name === "AsyncFunction";
}
function Bt(e, t) {
  Object.entries(e).forEach(([n, r]) => t(r, n));
}
function Ge(e, t) {
  return An(e, {
    valueFn: t
  });
}
function An(e, t) {
  const { valueFn: n, keyFn: r } = t;
  return Object.fromEntries(
    Object.entries(e).map(([o, s], i) => [
      r ? r(o, s) : o,
      n(s, o, i)
    ])
  );
}
function So(e, t, n) {
  if (Array.isArray(t)) {
    const [o, ...s] = t;
    switch (o) {
      case "!":
        return !e;
      case "+":
        return e + s[0];
      case "~+":
        return s[0] + e;
    }
  }
  const r = Vo(t);
  return e[r];
}
function Vo(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      throw new Error("No bindable function provided");
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function Ro(e, t, n) {
  return t.reduce(
    (r, o) => So(r, o),
    e
  );
}
function Po(e, t) {
  return t ? t.reduce((n, r) => n[r], e) : e;
}
const Co = window.structuredClone || ((e) => JSON.parse(JSON.stringify(e)));
function Ot(e) {
  return typeof e == "function" ? e : Co(vn(e));
}
function kt(e) {
  return e !== null && typeof e == "object" && e.nodeType === 1 && typeof e.nodeName == "string";
}
class No {
  toString() {
    return "";
  }
}
const De = new No();
function ve(e) {
  return vn(e) === De;
}
function Oo(e) {
  return Array.isArray(e) && e[0] === "bind";
}
function ko(e) {
  return e[1];
}
function $n(e, t, n) {
  if (Array.isArray(t)) {
    const [o, ...s] = t;
    switch (o) {
      case "!":
        return !e;
      case "+":
        return e + s[0];
      case "~+":
        return s[0] + e;
    }
  }
  const r = In(t, n);
  return e[r];
}
function In(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      if (!t)
        throw new Error("No bindable function provided");
      return t(r[0]);
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function Tn(e, t, n) {
  return t.reduce(
    (r, o) => $n(r, o, n),
    e
  );
}
function Dn(e, t, n, r) {
  t.reduce((o, s, i) => {
    if (i === t.length - 1)
      o[In(s, r)] = n;
    else
      return $n(o, s, r);
  }, e);
}
function xo(e, t, n) {
  const { paths: r, getBindableValueFn: o } = t, { paths: s, getBindableValueFn: i } = t;
  return r === void 0 || r.length === 0 ? e : fe(() => ({
    get() {
      try {
        return Tn(
          $e(e),
          r,
          o
        );
      } catch {
        return;
      }
    },
    set(c) {
      Dn(
        $e(e),
        s || r,
        c,
        i
      );
    }
  }));
}
function Ht(e, t) {
  return !ve(e) && JSON.stringify(t) === JSON.stringify(e);
}
function xt(e) {
  if (Pt(e)) {
    const t = e;
    return fe(() => ({
      get() {
        return $e(t);
      },
      set(n) {
        const r = $e(t);
        Ht(r, n) || (t.value = n);
      }
    }));
  }
  return fe((t, n) => ({
    get() {
      return t(), e;
    },
    set(r) {
      Ht(e, r) || (e = r, n());
    }
  }));
}
function Ao(e) {
  const { type: t, key: n, value: r } = e.args;
  return t === "local" ? dt(n, r) : dt(n, r, sessionStorage);
}
function $o(e) {
  const { storageKey: t = "insta-color-scheme" } = e.args;
  return Eo({
    valueDark: "insta-dark",
    storageKey: t
  });
}
const Io = /* @__PURE__ */ new Map([
  ["storage", Ao],
  ["useDark", $o]
]);
function To(e) {
  const { type: t } = e;
  if (!t)
    throw new Error("Invalid ref type");
  const n = Io.get(t);
  if (!n)
    throw new Error(`Invalid ref type ${t}`);
  return n(e);
}
function Do(e, t) {
  const { deepCompare: n = !1, type: r } = e;
  if (!r) {
    const { value: o } = e;
    return n ? xt(o) : G(o);
  }
  return To(e);
}
function Mo(e, t, n) {
  const { bind: r = {}, code: o, const: s = [] } = e, i = Object.values(r).map((l, a) => s[a] === 1 ? l : t.getVueRefObject(l));
  if (xn(new Function(o)))
    return co(
      async () => {
        const l = Object.fromEntries(
          Object.keys(r).map((a, f) => [a, i[f]])
        );
        return await K(o, l)();
      },
      null,
      { lazy: !0 }
    );
  const c = Object.fromEntries(
    Object.keys(r).map((l, a) => [l, i[a]])
  ), u = K(o, c);
  return I(u);
}
function jo(e) {
  const { init: t, deepEqOnInput: n } = e;
  return n === void 0 ? Q(t ?? De) : xt(t ?? De);
}
function Lo(e, t, n) {
  const {
    inputs: r = [],
    code: o,
    slient: s,
    data: i,
    asyncInit: c = null,
    deepEqOnInput: u = 0
  } = e, d = s || Array(r.length).fill(0), l = i || Array(r.length).fill(0), a = r.filter((v, y) => d[y] === 0 && l[y] === 0).map((v) => t.getVueRefObject(v));
  function f() {
    return r.map((v, y) => {
      if (l[y] === 1)
        return v;
      const w = t.getValue(v);
      return kt(w) ? w : Ot(w);
    });
  }
  const h = K(o), g = u === 0 ? Q(De) : xt(De), m = { immediate: !0, deep: !0 };
  return xn(h) ? (g.value = c, q(
    a,
    async () => {
      f().some(ve) || (g.value = await h(...f()));
    },
    m
  )) : q(
    a,
    () => {
      const v = f();
      v.some(ve) || (g.value = h(...v));
    },
    m
  ), Rt(g);
}
function Mn(e) {
  return !("type" in e);
}
function Wo(e) {
  return "type" in e && e.type === "rp";
}
function At(e) {
  return "sid" in e && "id" in e;
}
class Fo extends Map {
  constructor(t) {
    super(), this.factory = t;
  }
  getOrDefault(t) {
    if (!this.has(t)) {
      const n = this.factory();
      return this.set(t, n), n;
    }
    return super.get(t);
  }
}
function $t(e) {
  return new Fo(e);
}
class Bo {
  async eventSend(t, n) {
    const { fType: r, hKey: o, key: s } = t, i = lt().webServerInfo, c = s !== void 0 ? { key: s } : {}, u = r === "sync" ? i.event_url : i.event_async_url;
    let d = {};
    const l = await fetch(u, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        bind: n,
        hKey: o,
        ...c,
        page: Be(),
        ...d
      })
    });
    if (!l.ok)
      throw new Error(`HTTP error! status: ${l.status}`);
    return await l.json();
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, o = lt().webServerInfo, s = n === "sync" ? o.watch_url : o.watch_async_url, i = t.getServerInputs(), c = {
      key: r,
      input: i,
      page: Be()
    };
    return await (await fetch(s, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(c)
    })).json();
  }
}
class Ho {
  async eventSend(t, n) {
    const { fType: r, hKey: o, key: s } = t, i = s !== void 0 ? { key: s } : {};
    let c = {};
    const u = {
      bind: n,
      fType: r,
      hKey: o,
      ...i,
      page: Be(),
      ...c
    };
    return await window.pywebview.api.event_call(u);
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, o = t.getServerInputs(), s = {
      key: r,
      input: o,
      fType: n,
      page: Be()
    };
    return await window.pywebview.api.watch_call(s);
  }
}
let ht;
function zo(e) {
  switch (e) {
    case "web":
      ht = new Bo();
      break;
    case "webview":
      ht = new Ho();
      break;
  }
}
function jn() {
  return ht;
}
var ee = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.EventContext = 1] = "EventContext", e[e.Data = 2] = "Data", e[e.JsFn = 3] = "JsFn", e))(ee || {}), pt = /* @__PURE__ */ ((e) => (e.const = "c", e.ref = "r", e.range = "n", e))(pt || {}), Ee = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.RouterAction = 1] = "RouterAction", e[e.ElementRefAction = 2] = "ElementRefAction", e[e.JsCode = 3] = "JsCode", e))(Ee || {});
function Uo(e, t) {
  const r = {
    ref: {
      id: t.id,
      sid: e
    },
    type: Ee.Ref
  };
  return {
    ...t,
    immediate: !0,
    outputs: [r, ...t.outputs || []]
  };
}
function Ln(e) {
  const { config: t, varGetter: n } = e;
  if (!t)
    return {
      run: () => {
      },
      tryReset: () => {
      }
    };
  const r = t.map((i) => {
    const [c, u, d] = i, l = n.getVueRefObject(c);
    function a(f, h) {
      const { type: g, value: m } = h;
      if (g === "const") {
        f.value = m;
        return;
      }
      if (g === "action") {
        const v = Go(m, n);
        f.value = v;
        return;
      }
    }
    return {
      run: () => a(l, u),
      reset: () => a(l, d)
    };
  });
  return {
    run: () => {
      r.forEach((i) => i.run());
    },
    tryReset: () => {
      r.forEach((i) => i.reset());
    }
  };
}
function Go(e, t) {
  const { inputs: n = [], code: r } = e, o = K(r), s = n.map((i) => t.getValue(i));
  return o(...s);
}
function zt(e) {
  return e == null;
}
function Ke(e, t, n) {
  if (zt(t) || zt(e.values))
    return;
  t = t;
  const r = e.values, o = e.types ?? Array.from({ length: t.length }).fill(0);
  t.forEach((s, i) => {
    const c = o[i];
    if (c === 1)
      return;
    if (s.type === Ee.Ref) {
      if (c === 2) {
        r[i].forEach(([l, a]) => {
          const f = s.ref, h = {
            ...f,
            path: [...f.path ?? [], ...l]
          };
          n.updateValue(h, a);
        });
        return;
      }
      n.updateValue(s.ref, r[i]);
      return;
    }
    if (s.type === Ee.RouterAction) {
      const d = r[i], l = n.getRouter()[d.fn];
      l(...d.args);
      return;
    }
    if (s.type === Ee.ElementRefAction) {
      const d = s.ref, l = n.getVueRefObject(d).value, a = r[i], { method: f, args: h = [] } = a;
      l[f](...h);
      return;
    }
    if (s.type === Ee.JsCode) {
      const d = r[i];
      if (!d)
        return;
      const l = K(d);
      Promise.resolve(l());
      return;
    }
    const u = n.getVueRefObject(
      s.ref
    );
    u.value = r[i];
  });
}
function Ko(e) {
  const { watchConfigs: t, computedConfigs: n, varMapGetter: r, sid: o } = e;
  return new qo(t, n, r, o);
}
class qo {
  constructor(t, n, r, o) {
    H(this, "taskQueue", []);
    H(this, "id2TaskMap", /* @__PURE__ */ new Map());
    H(this, "input2TaskIdMap", $t(() => []));
    this.varMapGetter = r;
    const s = [], i = (c) => {
      var d;
      const u = new Jo(c, r);
      return this.id2TaskMap.set(u.id, u), (d = c.inputs) == null || d.forEach((l, a) => {
        var h, g;
        if (((h = c.data) == null ? void 0 : h[a]) === 0 && ((g = c.slient) == null ? void 0 : g[a]) === 0) {
          if (!Mn(l))
            throw new Error("Non-var input bindings are not supported.");
          const m = `${l.sid}-${l.id}`;
          this.input2TaskIdMap.getOrDefault(m).push(u.id);
        }
      }), u;
    };
    t == null || t.forEach((c) => {
      const u = i(c);
      s.push(u);
    }), n == null || n.forEach((c) => {
      const u = i(
        Uo(o, c)
      );
      s.push(u);
    }), s.forEach((c) => {
      const {
        deep: u = !0,
        once: d,
        flush: l,
        immediate: a = !0
      } = c.watchConfig, f = {
        immediate: a,
        deep: u,
        once: d,
        flush: l
      }, h = this._getWatchTargets(c);
      q(
        h,
        (g) => {
          g.some(ve) || (c.modify = !0, this.taskQueue.push(new Qo(c)), this._scheduleNextTick());
        },
        f
      );
    });
  }
  _getWatchTargets(t) {
    if (!t.watchConfig.inputs)
      return [];
    const n = t.slientInputs, r = t.constDataInputs;
    return t.watchConfig.inputs.filter(
      (s, i) => !r[i] && !n[i]
    ).map((s) => this.varMapGetter.getVueRefObject(s));
  }
  _scheduleNextTick() {
    Se(() => this._runAllTasks());
  }
  _runAllTasks() {
    const t = this.taskQueue.slice();
    this.taskQueue.length = 0, this._setTaskNodeRelations(t), t.forEach((n) => {
      n.run();
    });
  }
  _setTaskNodeRelations(t) {
    t.forEach((n) => {
      const r = this._findNextNodes(n, t);
      n.appendNextNodes(...r), r.forEach((o) => {
        o.appendPrevNodes(n);
      });
    });
  }
  _findNextNodes(t, n) {
    const r = t.watchTask.watchConfig.outputs;
    if (r && r.length <= 0)
      return [];
    const o = this._getCalculatorTasksByOutput(
      t.watchTask.watchConfig.outputs
    );
    return n.filter(
      (s) => o.has(s.watchTask.id) && s.watchTask.id !== t.watchTask.id
    );
  }
  _getCalculatorTasksByOutput(t) {
    const n = /* @__PURE__ */ new Set();
    return t == null || t.forEach((r) => {
      if (!At(r.ref))
        throw new Error("Non-var output bindings are not supported.");
      const { sid: o, id: s } = r.ref, i = `${o}-${s}`;
      (this.input2TaskIdMap.get(i) || []).forEach((u) => n.add(u));
    }), n;
  }
}
class Jo {
  constructor(t, n) {
    H(this, "modify", !0);
    H(this, "_running", !1);
    H(this, "id");
    H(this, "_runningPromise", null);
    H(this, "_runningPromiseResolve", null);
    H(this, "_inputInfos");
    this.watchConfig = t, this.varMapGetter = n, this.id = Symbol(t.debug), this._inputInfos = this.createInputInfos();
  }
  createInputInfos() {
    const { inputs: t = [] } = this.watchConfig, n = this.watchConfig.data || Array.from({ length: t.length }).fill(0), r = this.watchConfig.slient || Array.from({ length: t.length }).fill(0);
    return {
      const_data: n,
      slients: r
    };
  }
  get slientInputs() {
    return this._inputInfos.slients;
  }
  get constDataInputs() {
    return this._inputInfos.const_data;
  }
  getServerInputs() {
    const { const_data: t } = this._inputInfos;
    return this.watchConfig.inputs ? this.watchConfig.inputs.map((n, r) => t[r] === 0 ? this.varMapGetter.getValue(n) : n) : [];
  }
  get running() {
    return this._running;
  }
  get runningPromise() {
    return this._runningPromise;
  }
  /**
   * setRunning
   */
  setRunning() {
    this._running = !0, this._runningPromise = new Promise((t) => {
      this._runningPromiseResolve = t;
    });
  }
  /**
   * taskDone
   */
  taskDone() {
    this._running = !1, this._runningPromiseResolve && (this._runningPromiseResolve(), this._runningPromiseResolve = null);
  }
}
class Qo {
  /**
   *
   */
  constructor(t) {
    H(this, "prevNodes", []);
    H(this, "nextNodes", []);
    H(this, "_runningPrev", !1);
    this.watchTask = t;
  }
  /**
   * appendPrevNodes
   */
  appendPrevNodes(...t) {
    this.prevNodes.push(...t);
  }
  /**
   *
   */
  appendNextNodes(...t) {
    this.nextNodes.push(...t);
  }
  /**
   * hasNextNodes
   */
  hasNextNodes() {
    return this.nextNodes.length > 0;
  }
  /**
   * run
   */
  async run() {
    if (this.prevNodes.length > 0 && !this._runningPrev)
      try {
        this._runningPrev = !0, await Promise.all(this.prevNodes.map((t) => t.run()));
      } finally {
        this._runningPrev = !1;
      }
    if (this.watchTask.running) {
      await this.watchTask.runningPromise;
      return;
    }
    if (this.watchTask.modify) {
      this.watchTask.modify = !1, this.watchTask.setRunning();
      try {
        await Yo(this.watchTask);
      } finally {
        this.watchTask.taskDone();
      }
    }
  }
}
async function Yo(e) {
  const { varMapGetter: t } = e, { outputs: n, preSetup: r } = e.watchConfig, o = Ln({
    config: r,
    varGetter: t
  });
  try {
    o.run(), e.taskDone();
    const s = await jn().watchSend(e);
    if (!s)
      return;
    Ke(s, n, t);
  } finally {
    o.tryReset();
  }
}
function Xo(e, t) {
  const {
    on: n,
    code: r,
    immediate: o,
    deep: s,
    once: i,
    flush: c,
    bind: u = {},
    onData: d,
    bindData: l
  } = e, a = d || Array.from({ length: n.length }).fill(0), f = l || Array.from({ length: Object.keys(u).length }).fill(0), h = Ge(
    u,
    (v, y, w) => f[w] === 0 ? t.getVueRefObject(v) : v
  ), g = K(r, h), m = n.length === 1 ? Ut(a[0] === 1, n[0], t) : n.map(
    (v, y) => Ut(a[y] === 1, v, t)
  );
  return q(m, g, { immediate: o, deep: s, once: i, flush: c });
}
function Ut(e, t, n) {
  return e ? () => t : n.getVueRefObject(t);
}
function Zo(e, t) {
  const {
    inputs: n = [],
    outputs: r,
    slient: o,
    data: s,
    code: i,
    immediate: c = !0,
    deep: u,
    once: d,
    flush: l
  } = e, a = o || Array.from({ length: n.length }).fill(0), f = s || Array.from({ length: n.length }).fill(0), h = K(i), g = n.filter((v, y) => a[y] === 0 && f[y] === 0).map((v) => t.getVueRefObject(v));
  function m() {
    return n.map((v, y) => {
      if (f[y] === 0) {
        const w = t.getValue(v);
        return kt(w) ? w : Ot(w);
      }
      return v;
    });
  }
  q(
    g,
    () => {
      let v = h(...m());
      if (!r)
        return;
      const w = r.length === 1 ? [v] : v, b = w.map((V) => V === void 0 ? 1 : 0);
      Ke(
        {
          values: w,
          types: b
        },
        r,
        t
      );
    },
    { immediate: c, deep: u, once: d, flush: l }
  );
}
const gt = $t(() => Symbol());
function es(e, t) {
  const n = e.sid, r = gt.getOrDefault(n);
  gt.set(n, r), be(r, t);
}
function ts(e) {
  const t = gt.get(e);
  return te(t);
}
function ns() {
  return Wn().__VUE_DEVTOOLS_GLOBAL_HOOK__;
}
function Wn() {
  return typeof navigator < "u" && typeof window < "u" ? window : typeof globalThis < "u" ? globalThis : {};
}
const rs = typeof Proxy == "function", os = "devtools-plugin:setup", ss = "plugin:settings:set";
let _e, mt;
function is() {
  var e;
  return _e !== void 0 || (typeof window < "u" && window.performance ? (_e = !0, mt = window.performance) : typeof globalThis < "u" && (!((e = globalThis.perf_hooks) === null || e === void 0) && e.performance) ? (_e = !0, mt = globalThis.perf_hooks.performance) : _e = !1), _e;
}
function as() {
  return is() ? mt.now() : Date.now();
}
class cs {
  constructor(t, n) {
    this.target = null, this.targetQueue = [], this.onQueue = [], this.plugin = t, this.hook = n;
    const r = {};
    if (t.settings)
      for (const i in t.settings) {
        const c = t.settings[i];
        r[i] = c.defaultValue;
      }
    const o = `__vue-devtools-plugin-settings__${t.id}`;
    let s = Object.assign({}, r);
    try {
      const i = localStorage.getItem(o), c = JSON.parse(i);
      Object.assign(s, c);
    } catch {
    }
    this.fallbacks = {
      getSettings() {
        return s;
      },
      setSettings(i) {
        try {
          localStorage.setItem(o, JSON.stringify(i));
        } catch {
        }
        s = i;
      },
      now() {
        return as();
      }
    }, n && n.on(ss, (i, c) => {
      i === this.plugin.id && this.fallbacks.setSettings(c);
    }), this.proxiedOn = new Proxy({}, {
      get: (i, c) => this.target ? this.target.on[c] : (...u) => {
        this.onQueue.push({
          method: c,
          args: u
        });
      }
    }), this.proxiedTarget = new Proxy({}, {
      get: (i, c) => this.target ? this.target[c] : c === "on" ? this.proxiedOn : Object.keys(this.fallbacks).includes(c) ? (...u) => (this.targetQueue.push({
        method: c,
        args: u,
        resolve: () => {
        }
      }), this.fallbacks[c](...u)) : (...u) => new Promise((d) => {
        this.targetQueue.push({
          method: c,
          args: u,
          resolve: d
        });
      })
    });
  }
  async setRealTarget(t) {
    this.target = t;
    for (const n of this.onQueue)
      this.target.on[n.method](...n.args);
    for (const n of this.targetQueue)
      n.resolve(await this.target[n.method](...n.args));
  }
}
function ls(e, t) {
  const n = e, r = Wn(), o = ns(), s = rs && n.enableEarlyProxy;
  if (o && (r.__VUE_DEVTOOLS_PLUGIN_API_AVAILABLE__ || !s))
    o.emit(os, e, t);
  else {
    const i = s ? new cs(n, o) : null;
    (r.__VUE_DEVTOOLS_PLUGINS__ = r.__VUE_DEVTOOLS_PLUGINS__ || []).push({
      pluginDescriptor: n,
      setupFn: t,
      proxy: i
    }), i && t(i.proxiedTarget);
  }
}
var R = {};
const oe = typeof document < "u";
function Fn(e) {
  return typeof e == "object" || "displayName" in e || "props" in e || "__vccOpts" in e;
}
function us(e) {
  return e.__esModule || e[Symbol.toStringTag] === "Module" || // support CF with dynamic imports that do not
  // add the Module string tag
  e.default && Fn(e.default);
}
const k = Object.assign;
function nt(e, t) {
  const n = {};
  for (const r in t) {
    const o = t[r];
    n[r] = J(o) ? o.map(e) : e(o);
  }
  return n;
}
const ke = () => {
}, J = Array.isArray;
function P(e) {
  const t = Array.from(arguments).slice(1);
  console.warn.apply(console, ["[Vue Router warn]: " + e].concat(t));
}
const Bn = /#/g, fs = /&/g, ds = /\//g, hs = /=/g, ps = /\?/g, Hn = /\+/g, gs = /%5B/g, ms = /%5D/g, zn = /%5E/g, vs = /%60/g, Un = /%7B/g, ys = /%7C/g, Gn = /%7D/g, ws = /%20/g;
function It(e) {
  return encodeURI("" + e).replace(ys, "|").replace(gs, "[").replace(ms, "]");
}
function _s(e) {
  return It(e).replace(Un, "{").replace(Gn, "}").replace(zn, "^");
}
function vt(e) {
  return It(e).replace(Hn, "%2B").replace(ws, "+").replace(Bn, "%23").replace(fs, "%26").replace(vs, "`").replace(Un, "{").replace(Gn, "}").replace(zn, "^");
}
function Es(e) {
  return vt(e).replace(hs, "%3D");
}
function bs(e) {
  return It(e).replace(Bn, "%23").replace(ps, "%3F");
}
function Ss(e) {
  return e == null ? "" : bs(e).replace(ds, "%2F");
}
function Ve(e) {
  try {
    return decodeURIComponent("" + e);
  } catch {
    R.NODE_ENV !== "production" && P(`Error decoding "${e}". Using original value`);
  }
  return "" + e;
}
const Vs = /\/$/, Rs = (e) => e.replace(Vs, "");
function rt(e, t, n = "/") {
  let r, o = {}, s = "", i = "";
  const c = t.indexOf("#");
  let u = t.indexOf("?");
  return c < u && c >= 0 && (u = -1), u > -1 && (r = t.slice(0, u), s = t.slice(u + 1, c > -1 ? c : t.length), o = e(s)), c > -1 && (r = r || t.slice(0, c), i = t.slice(c, t.length)), r = Ns(r ?? t, n), {
    fullPath: r + (s && "?") + s + i,
    path: r,
    query: o,
    hash: Ve(i)
  };
}
function Ps(e, t) {
  const n = t.query ? e(t.query) : "";
  return t.path + (n && "?") + n + (t.hash || "");
}
function Gt(e, t) {
  return !t || !e.toLowerCase().startsWith(t.toLowerCase()) ? e : e.slice(t.length) || "/";
}
function Kt(e, t, n) {
  const r = t.matched.length - 1, o = n.matched.length - 1;
  return r > -1 && r === o && de(t.matched[r], n.matched[o]) && Kn(t.params, n.params) && e(t.query) === e(n.query) && t.hash === n.hash;
}
function de(e, t) {
  return (e.aliasOf || e) === (t.aliasOf || t);
}
function Kn(e, t) {
  if (Object.keys(e).length !== Object.keys(t).length)
    return !1;
  for (const n in e)
    if (!Cs(e[n], t[n]))
      return !1;
  return !0;
}
function Cs(e, t) {
  return J(e) ? qt(e, t) : J(t) ? qt(t, e) : e === t;
}
function qt(e, t) {
  return J(t) ? e.length === t.length && e.every((n, r) => n === t[r]) : e.length === 1 && e[0] === t;
}
function Ns(e, t) {
  if (e.startsWith("/"))
    return e;
  if (R.NODE_ENV !== "production" && !t.startsWith("/"))
    return P(`Cannot resolve a relative location without an absolute path. Trying to resolve "${e}" from "${t}". It should look like "/${t}".`), e;
  if (!e)
    return t;
  const n = t.split("/"), r = e.split("/"), o = r[r.length - 1];
  (o === ".." || o === ".") && r.push("");
  let s = n.length - 1, i, c;
  for (i = 0; i < r.length; i++)
    if (c = r[i], c !== ".")
      if (c === "..")
        s > 1 && s--;
      else
        break;
  return n.slice(0, s).join("/") + "/" + r.slice(i).join("/");
}
const le = {
  path: "/",
  // TODO: could we use a symbol in the future?
  name: void 0,
  params: {},
  query: {},
  hash: "",
  fullPath: "/",
  matched: [],
  meta: {},
  redirectedFrom: void 0
};
var Re;
(function(e) {
  e.pop = "pop", e.push = "push";
})(Re || (Re = {}));
var me;
(function(e) {
  e.back = "back", e.forward = "forward", e.unknown = "";
})(me || (me = {}));
const ot = "";
function qn(e) {
  if (!e)
    if (oe) {
      const t = document.querySelector("base");
      e = t && t.getAttribute("href") || "/", e = e.replace(/^\w+:\/\/[^\/]+/, "");
    } else
      e = "/";
  return e[0] !== "/" && e[0] !== "#" && (e = "/" + e), Rs(e);
}
const Os = /^[^#]+#/;
function Jn(e, t) {
  return e.replace(Os, "#") + t;
}
function ks(e, t) {
  const n = document.documentElement.getBoundingClientRect(), r = e.getBoundingClientRect();
  return {
    behavior: t.behavior,
    left: r.left - n.left - (t.left || 0),
    top: r.top - n.top - (t.top || 0)
  };
}
const qe = () => ({
  left: window.scrollX,
  top: window.scrollY
});
function xs(e) {
  let t;
  if ("el" in e) {
    const n = e.el, r = typeof n == "string" && n.startsWith("#");
    if (R.NODE_ENV !== "production" && typeof e.el == "string" && (!r || !document.getElementById(e.el.slice(1))))
      try {
        const s = document.querySelector(e.el);
        if (r && s) {
          P(`The selector "${e.el}" should be passed as "el: document.querySelector('${e.el}')" because it starts with "#".`);
          return;
        }
      } catch {
        P(`The selector "${e.el}" is invalid. If you are using an id selector, make sure to escape it. You can find more information about escaping characters in selectors at https://mathiasbynens.be/notes/css-escapes or use CSS.escape (https://developer.mozilla.org/en-US/docs/Web/API/CSS/escape).`);
        return;
      }
    const o = typeof n == "string" ? r ? document.getElementById(n.slice(1)) : document.querySelector(n) : n;
    if (!o) {
      R.NODE_ENV !== "production" && P(`Couldn't find element using selector "${e.el}" returned by scrollBehavior.`);
      return;
    }
    t = ks(o, e);
  } else
    t = e;
  "scrollBehavior" in document.documentElement.style ? window.scrollTo(t) : window.scrollTo(t.left != null ? t.left : window.scrollX, t.top != null ? t.top : window.scrollY);
}
function Jt(e, t) {
  return (history.state ? history.state.position - t : -1) + e;
}
const yt = /* @__PURE__ */ new Map();
function As(e, t) {
  yt.set(e, t);
}
function $s(e) {
  const t = yt.get(e);
  return yt.delete(e), t;
}
let Is = () => location.protocol + "//" + location.host;
function Qn(e, t) {
  const { pathname: n, search: r, hash: o } = t, s = e.indexOf("#");
  if (s > -1) {
    let c = o.includes(e.slice(s)) ? e.slice(s).length : 1, u = o.slice(c);
    return u[0] !== "/" && (u = "/" + u), Gt(u, "");
  }
  return Gt(n, e) + r + o;
}
function Ts(e, t, n, r) {
  let o = [], s = [], i = null;
  const c = ({ state: f }) => {
    const h = Qn(e, location), g = n.value, m = t.value;
    let v = 0;
    if (f) {
      if (n.value = h, t.value = f, i && i === g) {
        i = null;
        return;
      }
      v = m ? f.position - m.position : 0;
    } else
      r(h);
    o.forEach((y) => {
      y(n.value, g, {
        delta: v,
        type: Re.pop,
        direction: v ? v > 0 ? me.forward : me.back : me.unknown
      });
    });
  };
  function u() {
    i = n.value;
  }
  function d(f) {
    o.push(f);
    const h = () => {
      const g = o.indexOf(f);
      g > -1 && o.splice(g, 1);
    };
    return s.push(h), h;
  }
  function l() {
    const { history: f } = window;
    f.state && f.replaceState(k({}, f.state, { scroll: qe() }), "");
  }
  function a() {
    for (const f of s)
      f();
    s = [], window.removeEventListener("popstate", c), window.removeEventListener("beforeunload", l);
  }
  return window.addEventListener("popstate", c), window.addEventListener("beforeunload", l, {
    passive: !0
  }), {
    pauseListeners: u,
    listen: d,
    destroy: a
  };
}
function Qt(e, t, n, r = !1, o = !1) {
  return {
    back: e,
    current: t,
    forward: n,
    replaced: r,
    position: window.history.length,
    scroll: o ? qe() : null
  };
}
function Ds(e) {
  const { history: t, location: n } = window, r = {
    value: Qn(e, n)
  }, o = { value: t.state };
  o.value || s(r.value, {
    back: null,
    current: r.value,
    forward: null,
    // the length is off by one, we need to decrease it
    position: t.length - 1,
    replaced: !0,
    // don't add a scroll as the user may have an anchor, and we want
    // scrollBehavior to be triggered without a saved position
    scroll: null
  }, !0);
  function s(u, d, l) {
    const a = e.indexOf("#"), f = a > -1 ? (n.host && document.querySelector("base") ? e : e.slice(a)) + u : Is() + e + u;
    try {
      t[l ? "replaceState" : "pushState"](d, "", f), o.value = d;
    } catch (h) {
      R.NODE_ENV !== "production" ? P("Error with push/replace State", h) : console.error(h), n[l ? "replace" : "assign"](f);
    }
  }
  function i(u, d) {
    const l = k({}, t.state, Qt(
      o.value.back,
      // keep back and forward entries but override current position
      u,
      o.value.forward,
      !0
    ), d, { position: o.value.position });
    s(u, l, !0), r.value = u;
  }
  function c(u, d) {
    const l = k(
      {},
      // use current history state to gracefully handle a wrong call to
      // history.replaceState
      // https://github.com/vuejs/router/issues/366
      o.value,
      t.state,
      {
        forward: u,
        scroll: qe()
      }
    );
    R.NODE_ENV !== "production" && !t.state && P(`history.state seems to have been manually replaced without preserving the necessary values. Make sure to preserve existing history state if you are manually calling history.replaceState:

history.replaceState(history.state, '', url)

You can find more information at https://router.vuejs.org/guide/migration/#Usage-of-history-state`), s(l.current, l, !0);
    const a = k({}, Qt(r.value, u, null), { position: l.position + 1 }, d);
    s(u, a, !1), r.value = u;
  }
  return {
    location: r,
    state: o,
    push: c,
    replace: i
  };
}
function Yn(e) {
  e = qn(e);
  const t = Ds(e), n = Ts(e, t.state, t.location, t.replace);
  function r(s, i = !0) {
    i || n.pauseListeners(), history.go(s);
  }
  const o = k({
    // it's overridden right after
    location: "",
    base: e,
    go: r,
    createHref: Jn.bind(null, e)
  }, t, n);
  return Object.defineProperty(o, "location", {
    enumerable: !0,
    get: () => t.location.value
  }), Object.defineProperty(o, "state", {
    enumerable: !0,
    get: () => t.state.value
  }), o;
}
function Ms(e = "") {
  let t = [], n = [ot], r = 0;
  e = qn(e);
  function o(c) {
    r++, r !== n.length && n.splice(r), n.push(c);
  }
  function s(c, u, { direction: d, delta: l }) {
    const a = {
      direction: d,
      delta: l,
      type: Re.pop
    };
    for (const f of t)
      f(c, u, a);
  }
  const i = {
    // rewritten by Object.defineProperty
    location: ot,
    // TODO: should be kept in queue
    state: {},
    base: e,
    createHref: Jn.bind(null, e),
    replace(c) {
      n.splice(r--, 1), o(c);
    },
    push(c, u) {
      o(c);
    },
    listen(c) {
      return t.push(c), () => {
        const u = t.indexOf(c);
        u > -1 && t.splice(u, 1);
      };
    },
    destroy() {
      t = [], n = [ot], r = 0;
    },
    go(c, u = !0) {
      const d = this.location, l = (
        // we are considering delta === 0 going forward, but in abstract mode
        // using 0 for the delta doesn't make sense like it does in html5 where
        // it reloads the page
        c < 0 ? me.back : me.forward
      );
      r = Math.max(0, Math.min(r + c, n.length - 1)), u && s(this.location, d, {
        direction: l,
        delta: c
      });
    }
  };
  return Object.defineProperty(i, "location", {
    enumerable: !0,
    get: () => n[r]
  }), i;
}
function js(e) {
  return e = location.host ? e || location.pathname + location.search : "", e.includes("#") || (e += "#"), R.NODE_ENV !== "production" && !e.endsWith("#/") && !e.endsWith("#") && P(`A hash base must end with a "#":
"${e}" should be "${e.replace(/#.*$/, "#")}".`), Yn(e);
}
function He(e) {
  return typeof e == "string" || e && typeof e == "object";
}
function Xn(e) {
  return typeof e == "string" || typeof e == "symbol";
}
const wt = Symbol(R.NODE_ENV !== "production" ? "navigation failure" : "");
var Yt;
(function(e) {
  e[e.aborted = 4] = "aborted", e[e.cancelled = 8] = "cancelled", e[e.duplicated = 16] = "duplicated";
})(Yt || (Yt = {}));
const Ls = {
  1({ location: e, currentLocation: t }) {
    return `No match for
 ${JSON.stringify(e)}${t ? `
while being at
` + JSON.stringify(t) : ""}`;
  },
  2({ from: e, to: t }) {
    return `Redirected from "${e.fullPath}" to "${Fs(t)}" via a navigation guard.`;
  },
  4({ from: e, to: t }) {
    return `Navigation aborted from "${e.fullPath}" to "${t.fullPath}" via a navigation guard.`;
  },
  8({ from: e, to: t }) {
    return `Navigation cancelled from "${e.fullPath}" to "${t.fullPath}" with a new navigation.`;
  },
  16({ from: e, to: t }) {
    return `Avoided redundant navigation to current location: "${e.fullPath}".`;
  }
};
function Pe(e, t) {
  return R.NODE_ENV !== "production" ? k(new Error(Ls[e](t)), {
    type: e,
    [wt]: !0
  }, t) : k(new Error(), {
    type: e,
    [wt]: !0
  }, t);
}
function re(e, t) {
  return e instanceof Error && wt in e && (t == null || !!(e.type & t));
}
const Ws = ["params", "query", "hash"];
function Fs(e) {
  if (typeof e == "string")
    return e;
  if (e.path != null)
    return e.path;
  const t = {};
  for (const n of Ws)
    n in e && (t[n] = e[n]);
  return JSON.stringify(t, null, 2);
}
const Xt = "[^/]+?", Bs = {
  sensitive: !1,
  strict: !1,
  start: !0,
  end: !0
}, Hs = /[.+*?^${}()[\]/\\]/g;
function zs(e, t) {
  const n = k({}, Bs, t), r = [];
  let o = n.start ? "^" : "";
  const s = [];
  for (const d of e) {
    const l = d.length ? [] : [
      90
      /* PathScore.Root */
    ];
    n.strict && !d.length && (o += "/");
    for (let a = 0; a < d.length; a++) {
      const f = d[a];
      let h = 40 + (n.sensitive ? 0.25 : 0);
      if (f.type === 0)
        a || (o += "/"), o += f.value.replace(Hs, "\\$&"), h += 40;
      else if (f.type === 1) {
        const { value: g, repeatable: m, optional: v, regexp: y } = f;
        s.push({
          name: g,
          repeatable: m,
          optional: v
        });
        const w = y || Xt;
        if (w !== Xt) {
          h += 10;
          try {
            new RegExp(`(${w})`);
          } catch (V) {
            throw new Error(`Invalid custom RegExp for param "${g}" (${w}): ` + V.message);
          }
        }
        let b = m ? `((?:${w})(?:/(?:${w}))*)` : `(${w})`;
        a || (b = // avoid an optional / if there are more segments e.g. /:p?-static
        // or /:p?-:p2
        v && d.length < 2 ? `(?:/${b})` : "/" + b), v && (b += "?"), o += b, h += 20, v && (h += -8), m && (h += -20), w === ".*" && (h += -50);
      }
      l.push(h);
    }
    r.push(l);
  }
  if (n.strict && n.end) {
    const d = r.length - 1;
    r[d][r[d].length - 1] += 0.7000000000000001;
  }
  n.strict || (o += "/?"), n.end ? o += "$" : n.strict && !o.endsWith("/") && (o += "(?:/|$)");
  const i = new RegExp(o, n.sensitive ? "" : "i");
  function c(d) {
    const l = d.match(i), a = {};
    if (!l)
      return null;
    for (let f = 1; f < l.length; f++) {
      const h = l[f] || "", g = s[f - 1];
      a[g.name] = h && g.repeatable ? h.split("/") : h;
    }
    return a;
  }
  function u(d) {
    let l = "", a = !1;
    for (const f of e) {
      (!a || !l.endsWith("/")) && (l += "/"), a = !1;
      for (const h of f)
        if (h.type === 0)
          l += h.value;
        else if (h.type === 1) {
          const { value: g, repeatable: m, optional: v } = h, y = g in d ? d[g] : "";
          if (J(y) && !m)
            throw new Error(`Provided param "${g}" is an array but it is not repeatable (* or + modifiers)`);
          const w = J(y) ? y.join("/") : y;
          if (!w)
            if (v)
              f.length < 2 && (l.endsWith("/") ? l = l.slice(0, -1) : a = !0);
            else
              throw new Error(`Missing required param "${g}"`);
          l += w;
        }
    }
    return l || "/";
  }
  return {
    re: i,
    score: r,
    keys: s,
    parse: c,
    stringify: u
  };
}
function Us(e, t) {
  let n = 0;
  for (; n < e.length && n < t.length; ) {
    const r = t[n] - e[n];
    if (r)
      return r;
    n++;
  }
  return e.length < t.length ? e.length === 1 && e[0] === 80 ? -1 : 1 : e.length > t.length ? t.length === 1 && t[0] === 80 ? 1 : -1 : 0;
}
function Zn(e, t) {
  let n = 0;
  const r = e.score, o = t.score;
  for (; n < r.length && n < o.length; ) {
    const s = Us(r[n], o[n]);
    if (s)
      return s;
    n++;
  }
  if (Math.abs(o.length - r.length) === 1) {
    if (Zt(r))
      return 1;
    if (Zt(o))
      return -1;
  }
  return o.length - r.length;
}
function Zt(e) {
  const t = e[e.length - 1];
  return e.length > 0 && t[t.length - 1] < 0;
}
const Gs = {
  type: 0,
  value: ""
}, Ks = /[a-zA-Z0-9_]/;
function qs(e) {
  if (!e)
    return [[]];
  if (e === "/")
    return [[Gs]];
  if (!e.startsWith("/"))
    throw new Error(R.NODE_ENV !== "production" ? `Route paths should start with a "/": "${e}" should be "/${e}".` : `Invalid path "${e}"`);
  function t(h) {
    throw new Error(`ERR (${n})/"${d}": ${h}`);
  }
  let n = 0, r = n;
  const o = [];
  let s;
  function i() {
    s && o.push(s), s = [];
  }
  let c = 0, u, d = "", l = "";
  function a() {
    d && (n === 0 ? s.push({
      type: 0,
      value: d
    }) : n === 1 || n === 2 || n === 3 ? (s.length > 1 && (u === "*" || u === "+") && t(`A repeatable param (${d}) must be alone in its segment. eg: '/:ids+.`), s.push({
      type: 1,
      value: d,
      regexp: l,
      repeatable: u === "*" || u === "+",
      optional: u === "*" || u === "?"
    })) : t("Invalid state to consume buffer"), d = "");
  }
  function f() {
    d += u;
  }
  for (; c < e.length; ) {
    if (u = e[c++], u === "\\" && n !== 2) {
      r = n, n = 4;
      continue;
    }
    switch (n) {
      case 0:
        u === "/" ? (d && a(), i()) : u === ":" ? (a(), n = 1) : f();
        break;
      case 4:
        f(), n = r;
        break;
      case 1:
        u === "(" ? n = 2 : Ks.test(u) ? f() : (a(), n = 0, u !== "*" && u !== "?" && u !== "+" && c--);
        break;
      case 2:
        u === ")" ? l[l.length - 1] == "\\" ? l = l.slice(0, -1) + u : n = 3 : l += u;
        break;
      case 3:
        a(), n = 0, u !== "*" && u !== "?" && u !== "+" && c--, l = "";
        break;
      default:
        t("Unknown state");
        break;
    }
  }
  return n === 2 && t(`Unfinished custom RegExp for param "${d}"`), a(), i(), o;
}
function Js(e, t, n) {
  const r = zs(qs(e.path), n);
  if (R.NODE_ENV !== "production") {
    const s = /* @__PURE__ */ new Set();
    for (const i of r.keys)
      s.has(i.name) && P(`Found duplicated params with name "${i.name}" for path "${e.path}". Only the last one will be available on "$route.params".`), s.add(i.name);
  }
  const o = k(r, {
    record: e,
    parent: t,
    // these needs to be populated by the parent
    children: [],
    alias: []
  });
  return t && !o.record.aliasOf == !t.record.aliasOf && t.children.push(o), o;
}
function Qs(e, t) {
  const n = [], r = /* @__PURE__ */ new Map();
  t = rn({ strict: !1, end: !0, sensitive: !1 }, t);
  function o(a) {
    return r.get(a);
  }
  function s(a, f, h) {
    const g = !h, m = tn(a);
    R.NODE_ENV !== "production" && ei(m, f), m.aliasOf = h && h.record;
    const v = rn(t, a), y = [m];
    if ("alias" in a) {
      const V = typeof a.alias == "string" ? [a.alias] : a.alias;
      for (const A of V)
        y.push(
          // we need to normalize again to ensure the `mods` property
          // being non enumerable
          tn(k({}, m, {
            // this allows us to hold a copy of the `components` option
            // so that async components cache is hold on the original record
            components: h ? h.record.components : m.components,
            path: A,
            // we might be the child of an alias
            aliasOf: h ? h.record : m
            // the aliases are always of the same kind as the original since they
            // are defined on the same record
          }))
        );
    }
    let w, b;
    for (const V of y) {
      const { path: A } = V;
      if (f && A[0] !== "/") {
        const F = f.record.path, B = F[F.length - 1] === "/" ? "" : "/";
        V.path = f.record.path + (A && B + A);
      }
      if (R.NODE_ENV !== "production" && V.path === "*")
        throw new Error(`Catch all routes ("*") must now be defined using a param with a custom regexp.
See more at https://router.vuejs.org/guide/migration/#Removed-star-or-catch-all-routes.`);
      if (w = Js(V, f, v), R.NODE_ENV !== "production" && f && A[0] === "/" && ni(w, f), h ? (h.alias.push(w), R.NODE_ENV !== "production" && Zs(h, w)) : (b = b || w, b !== w && b.alias.push(w), g && a.name && !nn(w) && (R.NODE_ENV !== "production" && ti(a, f), i(a.name))), er(w) && u(w), m.children) {
        const F = m.children;
        for (let B = 0; B < F.length; B++)
          s(F[B], w, h && h.children[B]);
      }
      h = h || w;
    }
    return b ? () => {
      i(b);
    } : ke;
  }
  function i(a) {
    if (Xn(a)) {
      const f = r.get(a);
      f && (r.delete(a), n.splice(n.indexOf(f), 1), f.children.forEach(i), f.alias.forEach(i));
    } else {
      const f = n.indexOf(a);
      f > -1 && (n.splice(f, 1), a.record.name && r.delete(a.record.name), a.children.forEach(i), a.alias.forEach(i));
    }
  }
  function c() {
    return n;
  }
  function u(a) {
    const f = ri(a, n);
    n.splice(f, 0, a), a.record.name && !nn(a) && r.set(a.record.name, a);
  }
  function d(a, f) {
    let h, g = {}, m, v;
    if ("name" in a && a.name) {
      if (h = r.get(a.name), !h)
        throw Pe(1, {
          location: a
        });
      if (R.NODE_ENV !== "production") {
        const b = Object.keys(a.params || {}).filter((V) => !h.keys.find((A) => A.name === V));
        b.length && P(`Discarded invalid param(s) "${b.join('", "')}" when navigating. See https://github.com/vuejs/router/blob/main/packages/router/CHANGELOG.md#414-2022-08-22 for more details.`);
      }
      v = h.record.name, g = k(
        // paramsFromLocation is a new object
        en(
          f.params,
          // only keep params that exist in the resolved location
          // only keep optional params coming from a parent record
          h.keys.filter((b) => !b.optional).concat(h.parent ? h.parent.keys.filter((b) => b.optional) : []).map((b) => b.name)
        ),
        // discard any existing params in the current location that do not exist here
        // #1497 this ensures better active/exact matching
        a.params && en(a.params, h.keys.map((b) => b.name))
      ), m = h.stringify(g);
    } else if (a.path != null)
      m = a.path, R.NODE_ENV !== "production" && !m.startsWith("/") && P(`The Matcher cannot resolve relative paths but received "${m}". Unless you directly called \`matcher.resolve("${m}")\`, this is probably a bug in vue-router. Please open an issue at https://github.com/vuejs/router/issues/new/choose.`), h = n.find((b) => b.re.test(m)), h && (g = h.parse(m), v = h.record.name);
    else {
      if (h = f.name ? r.get(f.name) : n.find((b) => b.re.test(f.path)), !h)
        throw Pe(1, {
          location: a,
          currentLocation: f
        });
      v = h.record.name, g = k({}, f.params, a.params), m = h.stringify(g);
    }
    const y = [];
    let w = h;
    for (; w; )
      y.unshift(w.record), w = w.parent;
    return {
      name: v,
      path: m,
      params: g,
      matched: y,
      meta: Xs(y)
    };
  }
  e.forEach((a) => s(a));
  function l() {
    n.length = 0, r.clear();
  }
  return {
    addRoute: s,
    resolve: d,
    removeRoute: i,
    clearRoutes: l,
    getRoutes: c,
    getRecordMatcher: o
  };
}
function en(e, t) {
  const n = {};
  for (const r of t)
    r in e && (n[r] = e[r]);
  return n;
}
function tn(e) {
  const t = {
    path: e.path,
    redirect: e.redirect,
    name: e.name,
    meta: e.meta || {},
    aliasOf: e.aliasOf,
    beforeEnter: e.beforeEnter,
    props: Ys(e),
    children: e.children || [],
    instances: {},
    leaveGuards: /* @__PURE__ */ new Set(),
    updateGuards: /* @__PURE__ */ new Set(),
    enterCallbacks: {},
    // must be declared afterwards
    // mods: {},
    components: "components" in e ? e.components || null : e.component && { default: e.component }
  };
  return Object.defineProperty(t, "mods", {
    value: {}
  }), t;
}
function Ys(e) {
  const t = {}, n = e.props || !1;
  if ("component" in e)
    t.default = n;
  else
    for (const r in e.components)
      t[r] = typeof n == "object" ? n[r] : n;
  return t;
}
function nn(e) {
  for (; e; ) {
    if (e.record.aliasOf)
      return !0;
    e = e.parent;
  }
  return !1;
}
function Xs(e) {
  return e.reduce((t, n) => k(t, n.meta), {});
}
function rn(e, t) {
  const n = {};
  for (const r in e)
    n[r] = r in t ? t[r] : e[r];
  return n;
}
function _t(e, t) {
  return e.name === t.name && e.optional === t.optional && e.repeatable === t.repeatable;
}
function Zs(e, t) {
  for (const n of e.keys)
    if (!n.optional && !t.keys.find(_t.bind(null, n)))
      return P(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
  for (const n of t.keys)
    if (!n.optional && !e.keys.find(_t.bind(null, n)))
      return P(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
}
function ei(e, t) {
  t && t.record.name && !e.name && !e.path && P(`The route named "${String(t.record.name)}" has a child without a name and an empty path. Using that name won't render the empty path child so you probably want to move the name to the child instead. If this is intentional, add a name to the child route to remove the warning.`);
}
function ti(e, t) {
  for (let n = t; n; n = n.parent)
    if (n.record.name === e.name)
      throw new Error(`A route named "${String(e.name)}" has been added as a ${t === n ? "child" : "descendant"} of a route with the same name. Route names must be unique and a nested route cannot use the same name as an ancestor.`);
}
function ni(e, t) {
  for (const n of t.keys)
    if (!e.keys.find(_t.bind(null, n)))
      return P(`Absolute path "${e.record.path}" must have the exact same param named "${n.name}" as its parent "${t.record.path}".`);
}
function ri(e, t) {
  let n = 0, r = t.length;
  for (; n !== r; ) {
    const s = n + r >> 1;
    Zn(e, t[s]) < 0 ? r = s : n = s + 1;
  }
  const o = oi(e);
  return o && (r = t.lastIndexOf(o, r - 1), R.NODE_ENV !== "production" && r < 0 && P(`Finding ancestor route "${o.record.path}" failed for "${e.record.path}"`)), r;
}
function oi(e) {
  let t = e;
  for (; t = t.parent; )
    if (er(t) && Zn(e, t) === 0)
      return t;
}
function er({ record: e }) {
  return !!(e.name || e.components && Object.keys(e.components).length || e.redirect);
}
function si(e) {
  const t = {};
  if (e === "" || e === "?")
    return t;
  const r = (e[0] === "?" ? e.slice(1) : e).split("&");
  for (let o = 0; o < r.length; ++o) {
    const s = r[o].replace(Hn, " "), i = s.indexOf("="), c = Ve(i < 0 ? s : s.slice(0, i)), u = i < 0 ? null : Ve(s.slice(i + 1));
    if (c in t) {
      let d = t[c];
      J(d) || (d = t[c] = [d]), d.push(u);
    } else
      t[c] = u;
  }
  return t;
}
function on(e) {
  let t = "";
  for (let n in e) {
    const r = e[n];
    if (n = Es(n), r == null) {
      r !== void 0 && (t += (t.length ? "&" : "") + n);
      continue;
    }
    (J(r) ? r.map((s) => s && vt(s)) : [r && vt(r)]).forEach((s) => {
      s !== void 0 && (t += (t.length ? "&" : "") + n, s != null && (t += "=" + s));
    });
  }
  return t;
}
function ii(e) {
  const t = {};
  for (const n in e) {
    const r = e[n];
    r !== void 0 && (t[n] = J(r) ? r.map((o) => o == null ? null : "" + o) : r == null ? r : "" + r);
  }
  return t;
}
const ai = Symbol(R.NODE_ENV !== "production" ? "router view location matched" : ""), sn = Symbol(R.NODE_ENV !== "production" ? "router view depth" : ""), Je = Symbol(R.NODE_ENV !== "production" ? "router" : ""), Tt = Symbol(R.NODE_ENV !== "production" ? "route location" : ""), Et = Symbol(R.NODE_ENV !== "production" ? "router view location" : "");
function Ne() {
  let e = [];
  function t(r) {
    return e.push(r), () => {
      const o = e.indexOf(r);
      o > -1 && e.splice(o, 1);
    };
  }
  function n() {
    e = [];
  }
  return {
    add: t,
    list: () => e.slice(),
    reset: n
  };
}
function ue(e, t, n, r, o, s = (i) => i()) {
  const i = r && // name is defined if record is because of the function overload
  (r.enterCallbacks[o] = r.enterCallbacks[o] || []);
  return () => new Promise((c, u) => {
    const d = (f) => {
      f === !1 ? u(Pe(4, {
        from: n,
        to: t
      })) : f instanceof Error ? u(f) : He(f) ? u(Pe(2, {
        from: t,
        to: f
      })) : (i && // since enterCallbackArray is truthy, both record and name also are
      r.enterCallbacks[o] === i && typeof f == "function" && i.push(f), c());
    }, l = s(() => e.call(r && r.instances[o], t, n, R.NODE_ENV !== "production" ? ci(d, t, n) : d));
    let a = Promise.resolve(l);
    if (e.length < 3 && (a = a.then(d)), R.NODE_ENV !== "production" && e.length > 2) {
      const f = `The "next" callback was never called inside of ${e.name ? '"' + e.name + '"' : ""}:
${e.toString()}
. If you are returning a value instead of calling "next", make sure to remove the "next" parameter from your function.`;
      if (typeof l == "object" && "then" in l)
        a = a.then((h) => d._called ? h : (P(f), Promise.reject(new Error("Invalid navigation guard"))));
      else if (l !== void 0 && !d._called) {
        P(f), u(new Error("Invalid navigation guard"));
        return;
      }
    }
    a.catch((f) => u(f));
  });
}
function ci(e, t, n) {
  let r = 0;
  return function() {
    r++ === 1 && P(`The "next" callback was called more than once in one navigation guard when going from "${n.fullPath}" to "${t.fullPath}". It should be called exactly one time in each navigation guard. This will fail in production.`), e._called = !0, r === 1 && e.apply(null, arguments);
  };
}
function st(e, t, n, r, o = (s) => s()) {
  const s = [];
  for (const i of e) {
    R.NODE_ENV !== "production" && !i.components && !i.children.length && P(`Record with path "${i.path}" is either missing a "component(s)" or "children" property.`);
    for (const c in i.components) {
      let u = i.components[c];
      if (R.NODE_ENV !== "production") {
        if (!u || typeof u != "object" && typeof u != "function")
          throw P(`Component "${c}" in record with path "${i.path}" is not a valid component. Received "${String(u)}".`), new Error("Invalid route component");
        if ("then" in u) {
          P(`Component "${c}" in record with path "${i.path}" is a Promise instead of a function that returns a Promise. Did you write "import('./MyPage.vue')" instead of "() => import('./MyPage.vue')" ? This will break in production if not fixed.`);
          const d = u;
          u = () => d;
        } else u.__asyncLoader && // warn only once per component
        !u.__warnedDefineAsync && (u.__warnedDefineAsync = !0, P(`Component "${c}" in record with path "${i.path}" is defined using "defineAsyncComponent()". Write "() => import('./MyPage.vue')" instead of "defineAsyncComponent(() => import('./MyPage.vue'))".`));
      }
      if (!(t !== "beforeRouteEnter" && !i.instances[c]))
        if (Fn(u)) {
          const l = (u.__vccOpts || u)[t];
          l && s.push(ue(l, n, r, i, c, o));
        } else {
          let d = u();
          R.NODE_ENV !== "production" && !("catch" in d) && (P(`Component "${c}" in record with path "${i.path}" is a function that does not return a Promise. If you were passing a functional component, make sure to add a "displayName" to the component. This will break in production if not fixed.`), d = Promise.resolve(d)), s.push(() => d.then((l) => {
            if (!l)
              throw new Error(`Couldn't resolve component "${c}" at "${i.path}"`);
            const a = us(l) ? l.default : l;
            i.mods[c] = l, i.components[c] = a;
            const h = (a.__vccOpts || a)[t];
            return h && ue(h, n, r, i, c, o)();
          }));
        }
    }
  }
  return s;
}
function an(e) {
  const t = te(Je), n = te(Tt);
  let r = !1, o = null;
  const s = I(() => {
    const l = U(e.to);
    return R.NODE_ENV !== "production" && (!r || l !== o) && (He(l) || (r ? P(`Invalid value for prop "to" in useLink()
- to:`, l, `
- previous to:`, o, `
- props:`, e) : P(`Invalid value for prop "to" in useLink()
- to:`, l, `
- props:`, e)), o = l, r = !0), t.resolve(l);
  }), i = I(() => {
    const { matched: l } = s.value, { length: a } = l, f = l[a - 1], h = n.matched;
    if (!f || !h.length)
      return -1;
    const g = h.findIndex(de.bind(null, f));
    if (g > -1)
      return g;
    const m = cn(l[a - 2]);
    return (
      // we are dealing with nested routes
      a > 1 && // if the parent and matched route have the same path, this link is
      // referring to the empty child. Or we currently are on a different
      // child of the same parent
      cn(f) === m && // avoid comparing the child with its parent
      h[h.length - 1].path !== m ? h.findIndex(de.bind(null, l[a - 2])) : g
    );
  }), c = I(() => i.value > -1 && hi(n.params, s.value.params)), u = I(() => i.value > -1 && i.value === n.matched.length - 1 && Kn(n.params, s.value.params));
  function d(l = {}) {
    if (di(l)) {
      const a = t[U(e.replace) ? "replace" : "push"](
        U(e.to)
        // avoid uncaught errors are they are logged anyway
      ).catch(ke);
      return e.viewTransition && typeof document < "u" && "startViewTransition" in document && document.startViewTransition(() => a), a;
    }
    return Promise.resolve();
  }
  if (R.NODE_ENV !== "production" && oe) {
    const l = Ue();
    if (l) {
      const a = {
        route: s.value,
        isActive: c.value,
        isExactActive: u.value,
        error: null
      };
      l.__vrl_devtools = l.__vrl_devtools || [], l.__vrl_devtools.push(a), Ct(() => {
        a.route = s.value, a.isActive = c.value, a.isExactActive = u.value, a.error = He(U(e.to)) ? null : 'Invalid "to" value';
      }, { flush: "post" });
    }
  }
  return {
    route: s,
    href: I(() => s.value.href),
    isActive: c,
    isExactActive: u,
    navigate: d
  };
}
function li(e) {
  return e.length === 1 ? e[0] : e;
}
const ui = /* @__PURE__ */ j({
  name: "RouterLink",
  compatConfig: { MODE: 3 },
  props: {
    to: {
      type: [String, Object],
      required: !0
    },
    replace: Boolean,
    activeClass: String,
    // inactiveClass: String,
    exactActiveClass: String,
    custom: Boolean,
    ariaCurrentValue: {
      type: String,
      default: "page"
    }
  },
  useLink: an,
  setup(e, { slots: t }) {
    const n = Ir(an(e)), { options: r } = te(Je), o = I(() => ({
      [ln(e.activeClass, r.linkActiveClass, "router-link-active")]: n.isActive,
      // [getLinkClass(
      //   props.inactiveClass,
      //   options.linkInactiveClass,
      //   'router-link-inactive'
      // )]: !link.isExactActive,
      [ln(e.exactActiveClass, r.linkExactActiveClass, "router-link-exact-active")]: n.isExactActive
    }));
    return () => {
      const s = t.default && li(t.default(n));
      return e.custom ? s : D("a", {
        "aria-current": n.isExactActive ? e.ariaCurrentValue : null,
        href: n.href,
        // this would override user added attrs but Vue will still add
        // the listener, so we end up triggering both
        onClick: n.navigate,
        class: o.value
      }, s);
    };
  }
}), fi = ui;
function di(e) {
  if (!(e.metaKey || e.altKey || e.ctrlKey || e.shiftKey) && !e.defaultPrevented && !(e.button !== void 0 && e.button !== 0)) {
    if (e.currentTarget && e.currentTarget.getAttribute) {
      const t = e.currentTarget.getAttribute("target");
      if (/\b_blank\b/i.test(t))
        return;
    }
    return e.preventDefault && e.preventDefault(), !0;
  }
}
function hi(e, t) {
  for (const n in t) {
    const r = t[n], o = e[n];
    if (typeof r == "string") {
      if (r !== o)
        return !1;
    } else if (!J(o) || o.length !== r.length || r.some((s, i) => s !== o[i]))
      return !1;
  }
  return !0;
}
function cn(e) {
  return e ? e.aliasOf ? e.aliasOf.path : e.path : "";
}
const ln = (e, t, n) => e ?? t ?? n, pi = /* @__PURE__ */ j({
  name: "RouterView",
  // #674 we manually inherit them
  inheritAttrs: !1,
  props: {
    name: {
      type: String,
      default: "default"
    },
    route: Object
  },
  // Better compat for @vue/compat users
  // https://github.com/vuejs/router/issues/1315
  compatConfig: { MODE: 3 },
  setup(e, { attrs: t, slots: n }) {
    R.NODE_ENV !== "production" && mi();
    const r = te(Et), o = I(() => e.route || r.value), s = te(sn, 0), i = I(() => {
      let d = U(s);
      const { matched: l } = o.value;
      let a;
      for (; (a = l[d]) && !a.components; )
        d++;
      return d;
    }), c = I(() => o.value.matched[i.value]);
    be(sn, I(() => i.value + 1)), be(ai, c), be(Et, o);
    const u = G();
    return q(() => [u.value, c.value, e.name], ([d, l, a], [f, h, g]) => {
      l && (l.instances[a] = d, h && h !== l && d && d === f && (l.leaveGuards.size || (l.leaveGuards = h.leaveGuards), l.updateGuards.size || (l.updateGuards = h.updateGuards))), d && l && // if there is no instance but to and from are the same this might be
      // the first visit
      (!h || !de(l, h) || !f) && (l.enterCallbacks[a] || []).forEach((m) => m(d));
    }, { flush: "post" }), () => {
      const d = o.value, l = e.name, a = c.value, f = a && a.components[l];
      if (!f)
        return un(n.default, { Component: f, route: d });
      const h = a.props[l], g = h ? h === !0 ? d.params : typeof h == "function" ? h(d) : h : null, v = D(f, k({}, g, t, {
        onVnodeUnmounted: (y) => {
          y.component.isUnmounted && (a.instances[l] = null);
        },
        ref: u
      }));
      if (R.NODE_ENV !== "production" && oe && v.ref) {
        const y = {
          depth: i.value,
          name: a.name,
          path: a.path,
          meta: a.meta
        };
        (J(v.ref) ? v.ref.map((b) => b.i) : [v.ref.i]).forEach((b) => {
          b.__vrv_devtools = y;
        });
      }
      return (
        // pass the vnode to the slot as a prop.
        // h and <component :is="..."> both accept vnodes
        un(n.default, { Component: v, route: d }) || v
      );
    };
  }
});
function un(e, t) {
  if (!e)
    return null;
  const n = e(t);
  return n.length === 1 ? n[0] : n;
}
const gi = pi;
function mi() {
  const e = Ue(), t = e.parent && e.parent.type.name, n = e.parent && e.parent.subTree && e.parent.subTree.type;
  if (t && (t === "KeepAlive" || t.includes("Transition")) && typeof n == "object" && n.name === "RouterView") {
    const r = t === "KeepAlive" ? "keep-alive" : "transition";
    P(`<router-view> can no longer be used directly inside <transition> or <keep-alive>.
Use slot props instead:

<router-view v-slot="{ Component }">
  <${r}>
    <component :is="Component" />
  </${r}>
</router-view>`);
  }
}
function Oe(e, t) {
  const n = k({}, e, {
    // remove variables that can contain vue instances
    matched: e.matched.map((r) => Ci(r, ["instances", "children", "aliasOf"]))
  });
  return {
    _custom: {
      type: null,
      readOnly: !0,
      display: e.fullPath,
      tooltip: t,
      value: n
    }
  };
}
function Fe(e) {
  return {
    _custom: {
      display: e
    }
  };
}
let vi = 0;
function yi(e, t, n) {
  if (t.__hasDevtools)
    return;
  t.__hasDevtools = !0;
  const r = vi++;
  ls({
    id: "org.vuejs.router" + (r ? "." + r : ""),
    label: "Vue Router",
    packageName: "vue-router",
    homepage: "https://router.vuejs.org",
    logo: "https://router.vuejs.org/logo.png",
    componentStateTypes: ["Routing"],
    app: e
  }, (o) => {
    typeof o.now != "function" && console.warn("[Vue Router]: You seem to be using an outdated version of Vue Devtools. Are you still using the Beta release instead of the stable one? You can find the links at https://devtools.vuejs.org/guide/installation.html."), o.on.inspectComponent((l, a) => {
      l.instanceData && l.instanceData.state.push({
        type: "Routing",
        key: "$route",
        editable: !1,
        value: Oe(t.currentRoute.value, "Current Route")
      });
    }), o.on.visitComponentTree(({ treeNode: l, componentInstance: a }) => {
      if (a.__vrv_devtools) {
        const f = a.__vrv_devtools;
        l.tags.push({
          label: (f.name ? `${f.name.toString()}: ` : "") + f.path,
          textColor: 0,
          tooltip: "This component is rendered by &lt;router-view&gt;",
          backgroundColor: tr
        });
      }
      J(a.__vrl_devtools) && (a.__devtoolsApi = o, a.__vrl_devtools.forEach((f) => {
        let h = f.route.path, g = or, m = "", v = 0;
        f.error ? (h = f.error, g = Si, v = Vi) : f.isExactActive ? (g = rr, m = "This is exactly active") : f.isActive && (g = nr, m = "This link is active"), l.tags.push({
          label: h,
          textColor: v,
          tooltip: m,
          backgroundColor: g
        });
      }));
    }), q(t.currentRoute, () => {
      u(), o.notifyComponentUpdate(), o.sendInspectorTree(c), o.sendInspectorState(c);
    });
    const s = "router:navigations:" + r;
    o.addTimelineLayer({
      id: s,
      label: `Router${r ? " " + r : ""} Navigations`,
      color: 4237508
    }), t.onError((l, a) => {
      o.addTimelineEvent({
        layerId: s,
        event: {
          title: "Error during Navigation",
          subtitle: a.fullPath,
          logType: "error",
          time: o.now(),
          data: { error: l },
          groupId: a.meta.__navigationId
        }
      });
    });
    let i = 0;
    t.beforeEach((l, a) => {
      const f = {
        guard: Fe("beforeEach"),
        from: Oe(a, "Current Location during this navigation"),
        to: Oe(l, "Target location")
      };
      Object.defineProperty(l.meta, "__navigationId", {
        value: i++
      }), o.addTimelineEvent({
        layerId: s,
        event: {
          time: o.now(),
          title: "Start of navigation",
          subtitle: l.fullPath,
          data: f,
          groupId: l.meta.__navigationId
        }
      });
    }), t.afterEach((l, a, f) => {
      const h = {
        guard: Fe("afterEach")
      };
      f ? (h.failure = {
        _custom: {
          type: Error,
          readOnly: !0,
          display: f ? f.message : "",
          tooltip: "Navigation Failure",
          value: f
        }
      }, h.status = Fe("❌")) : h.status = Fe("✅"), h.from = Oe(a, "Current Location during this navigation"), h.to = Oe(l, "Target location"), o.addTimelineEvent({
        layerId: s,
        event: {
          title: "End of navigation",
          subtitle: l.fullPath,
          time: o.now(),
          data: h,
          logType: f ? "warning" : "default",
          groupId: l.meta.__navigationId
        }
      });
    });
    const c = "router-inspector:" + r;
    o.addInspector({
      id: c,
      label: "Routes" + (r ? " " + r : ""),
      icon: "book",
      treeFilterPlaceholder: "Search routes"
    });
    function u() {
      if (!d)
        return;
      const l = d;
      let a = n.getRoutes().filter((f) => !f.parent || // these routes have a parent with no component which will not appear in the view
      // therefore we still need to include them
      !f.parent.record.components);
      a.forEach(ar), l.filter && (a = a.filter((f) => (
        // save matches state based on the payload
        bt(f, l.filter.toLowerCase())
      ))), a.forEach((f) => ir(f, t.currentRoute.value)), l.rootNodes = a.map(sr);
    }
    let d;
    o.on.getInspectorTree((l) => {
      d = l, l.app === e && l.inspectorId === c && u();
    }), o.on.getInspectorState((l) => {
      if (l.app === e && l.inspectorId === c) {
        const f = n.getRoutes().find((h) => h.record.__vd_id === l.nodeId);
        f && (l.state = {
          options: _i(f)
        });
      }
    }), o.sendInspectorTree(c), o.sendInspectorState(c);
  });
}
function wi(e) {
  return e.optional ? e.repeatable ? "*" : "?" : e.repeatable ? "+" : "";
}
function _i(e) {
  const { record: t } = e, n = [
    { editable: !1, key: "path", value: t.path }
  ];
  return t.name != null && n.push({
    editable: !1,
    key: "name",
    value: t.name
  }), n.push({ editable: !1, key: "regexp", value: e.re }), e.keys.length && n.push({
    editable: !1,
    key: "keys",
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.keys.map((r) => `${r.name}${wi(r)}`).join(" "),
        tooltip: "Param keys",
        value: e.keys
      }
    }
  }), t.redirect != null && n.push({
    editable: !1,
    key: "redirect",
    value: t.redirect
  }), e.alias.length && n.push({
    editable: !1,
    key: "aliases",
    value: e.alias.map((r) => r.record.path)
  }), Object.keys(e.record.meta).length && n.push({
    editable: !1,
    key: "meta",
    value: e.record.meta
  }), n.push({
    key: "score",
    editable: !1,
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.score.map((r) => r.join(", ")).join(" | "),
        tooltip: "Score used to sort routes",
        value: e.score
      }
    }
  }), n;
}
const tr = 15485081, nr = 2450411, rr = 8702998, Ei = 2282478, or = 16486972, bi = 6710886, Si = 16704226, Vi = 12131356;
function sr(e) {
  const t = [], { record: n } = e;
  n.name != null && t.push({
    label: String(n.name),
    textColor: 0,
    backgroundColor: Ei
  }), n.aliasOf && t.push({
    label: "alias",
    textColor: 0,
    backgroundColor: or
  }), e.__vd_match && t.push({
    label: "matches",
    textColor: 0,
    backgroundColor: tr
  }), e.__vd_exactActive && t.push({
    label: "exact",
    textColor: 0,
    backgroundColor: rr
  }), e.__vd_active && t.push({
    label: "active",
    textColor: 0,
    backgroundColor: nr
  }), n.redirect && t.push({
    label: typeof n.redirect == "string" ? `redirect: ${n.redirect}` : "redirects",
    textColor: 16777215,
    backgroundColor: bi
  });
  let r = n.__vd_id;
  return r == null && (r = String(Ri++), n.__vd_id = r), {
    id: r,
    label: n.path,
    tags: t,
    children: e.children.map(sr)
  };
}
let Ri = 0;
const Pi = /^\/(.*)\/([a-z]*)$/;
function ir(e, t) {
  const n = t.matched.length && de(t.matched[t.matched.length - 1], e.record);
  e.__vd_exactActive = e.__vd_active = n, n || (e.__vd_active = t.matched.some((r) => de(r, e.record))), e.children.forEach((r) => ir(r, t));
}
function ar(e) {
  e.__vd_match = !1, e.children.forEach(ar);
}
function bt(e, t) {
  const n = String(e.re).match(Pi);
  if (e.__vd_match = !1, !n || n.length < 3)
    return !1;
  if (new RegExp(n[1].replace(/\$$/, ""), n[2]).test(t))
    return e.children.forEach((i) => bt(i, t)), e.record.path !== "/" || t === "/" ? (e.__vd_match = e.re.test(t), !0) : !1;
  const o = e.record.path.toLowerCase(), s = Ve(o);
  return !t.startsWith("/") && (s.includes(t) || o.includes(t)) || s.startsWith(t) || o.startsWith(t) || e.record.name && String(e.record.name).includes(t) ? !0 : e.children.some((i) => bt(i, t));
}
function Ci(e, t) {
  const n = {};
  for (const r in e)
    t.includes(r) || (n[r] = e[r]);
  return n;
}
function Ni(e) {
  const t = Qs(e.routes, e), n = e.parseQuery || si, r = e.stringifyQuery || on, o = e.history;
  if (R.NODE_ENV !== "production" && !o)
    throw new Error('Provide the "history" option when calling "createRouter()": https://router.vuejs.org/api/interfaces/RouterOptions.html#history');
  const s = Ne(), i = Ne(), c = Ne(), u = Q(le);
  let d = le;
  oe && e.scrollBehavior && "scrollRestoration" in history && (history.scrollRestoration = "manual");
  const l = nt.bind(null, (p) => "" + p), a = nt.bind(null, Ss), f = (
    // @ts-expect-error: intentionally avoid the type check
    nt.bind(null, Ve)
  );
  function h(p, E) {
    let _, S;
    return Xn(p) ? (_ = t.getRecordMatcher(p), R.NODE_ENV !== "production" && !_ && P(`Parent route "${String(p)}" not found when adding child route`, E), S = E) : S = p, t.addRoute(S, _);
  }
  function g(p) {
    const E = t.getRecordMatcher(p);
    E ? t.removeRoute(E) : R.NODE_ENV !== "production" && P(`Cannot remove non-existent route "${String(p)}"`);
  }
  function m() {
    return t.getRoutes().map((p) => p.record);
  }
  function v(p) {
    return !!t.getRecordMatcher(p);
  }
  function y(p, E) {
    if (E = k({}, E || u.value), typeof p == "string") {
      const C = rt(n, p, E.path), M = t.resolve({ path: C.path }, E), he = o.createHref(C.fullPath);
      return R.NODE_ENV !== "production" && (he.startsWith("//") ? P(`Location "${p}" resolved to "${he}". A resolved location cannot start with multiple slashes.`) : M.matched.length || P(`No match found for location with path "${p}"`)), k(C, M, {
        params: f(M.params),
        hash: Ve(C.hash),
        redirectedFrom: void 0,
        href: he
      });
    }
    if (R.NODE_ENV !== "production" && !He(p))
      return P(`router.resolve() was passed an invalid location. This will fail in production.
- Location:`, p), y({});
    let _;
    if (p.path != null)
      R.NODE_ENV !== "production" && "params" in p && !("name" in p) && // @ts-expect-error: the type is never
      Object.keys(p.params).length && P(`Path "${p.path}" was passed with params but they will be ignored. Use a named route alongside params instead.`), _ = k({}, p, {
        path: rt(n, p.path, E.path).path
      });
    else {
      const C = k({}, p.params);
      for (const M in C)
        C[M] == null && delete C[M];
      _ = k({}, p, {
        params: a(C)
      }), E.params = a(E.params);
    }
    const S = t.resolve(_, E), x = p.hash || "";
    R.NODE_ENV !== "production" && x && !x.startsWith("#") && P(`A \`hash\` should always start with the character "#". Replace "${x}" with "#${x}".`), S.params = l(f(S.params));
    const W = Ps(r, k({}, p, {
      hash: _s(x),
      path: S.path
    })), O = o.createHref(W);
    return R.NODE_ENV !== "production" && (O.startsWith("//") ? P(`Location "${p}" resolved to "${O}". A resolved location cannot start with multiple slashes.`) : S.matched.length || P(`No match found for location with path "${p.path != null ? p.path : p}"`)), k({
      fullPath: W,
      // keep the hash encoded so fullPath is effectively path + encodedQuery +
      // hash
      hash: x,
      query: (
        // if the user is using a custom query lib like qs, we might have
        // nested objects, so we keep the query as is, meaning it can contain
        // numbers at `$route.query`, but at the point, the user will have to
        // use their own type anyway.
        // https://github.com/vuejs/router/issues/328#issuecomment-649481567
        r === on ? ii(p.query) : p.query || {}
      )
    }, S, {
      redirectedFrom: void 0,
      href: O
    });
  }
  function w(p) {
    return typeof p == "string" ? rt(n, p, u.value.path) : k({}, p);
  }
  function b(p, E) {
    if (d !== p)
      return Pe(8, {
        from: E,
        to: p
      });
  }
  function V(p) {
    return B(p);
  }
  function A(p) {
    return V(k(w(p), { replace: !0 }));
  }
  function F(p) {
    const E = p.matched[p.matched.length - 1];
    if (E && E.redirect) {
      const { redirect: _ } = E;
      let S = typeof _ == "function" ? _(p) : _;
      if (typeof S == "string" && (S = S.includes("?") || S.includes("#") ? S = w(S) : (
        // force empty params
        { path: S }
      ), S.params = {}), R.NODE_ENV !== "production" && S.path == null && !("name" in S))
        throw P(`Invalid redirect found:
${JSON.stringify(S, null, 2)}
 when navigating to "${p.fullPath}". A redirect must contain a name or path. This will break in production.`), new Error("Invalid redirect");
      return k({
        query: p.query,
        hash: p.hash,
        // avoid transferring params if the redirect has a path
        params: S.path != null ? {} : p.params
      }, S);
    }
  }
  function B(p, E) {
    const _ = d = y(p), S = u.value, x = p.state, W = p.force, O = p.replace === !0, C = F(_);
    if (C)
      return B(
        k(w(C), {
          state: typeof C == "object" ? k({}, x, C.state) : x,
          force: W,
          replace: O
        }),
        // keep original redirectedFrom if it exists
        E || _
      );
    const M = _;
    M.redirectedFrom = E;
    let he;
    return !W && Kt(r, S, _) && (he = Pe(16, { to: M, from: S }), jt(
      S,
      S,
      // this is a push, the only way for it to be triggered from a
      // history.listen is with a redirect, which makes it become a push
      !0,
      // This cannot be the first navigation because the initial location
      // cannot be manually navigated to
      !1
    )), (he ? Promise.resolve(he) : N(M, S)).catch((z) => re(z) ? (
      // navigation redirects still mark the router as ready
      re(
        z,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? z : Xe(z)
    ) : (
      // reject any unknown error
      Ye(z, M, S)
    )).then((z) => {
      if (z) {
        if (re(
          z,
          2
          /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
        ))
          return R.NODE_ENV !== "production" && // we are redirecting to the same location we were already at
          Kt(r, y(z.to), M) && // and we have done it a couple of times
          E && // @ts-expect-error: added only in dev
          (E._count = E._count ? (
            // @ts-expect-error
            E._count + 1
          ) : 1) > 30 ? (P(`Detected a possibly infinite redirection in a navigation guard when going from "${S.fullPath}" to "${M.fullPath}". Aborting to avoid a Stack Overflow.
 Are you always returning a new location within a navigation guard? That would lead to this error. Only return when redirecting or aborting, that should fix this. This might break in production if not fixed.`), Promise.reject(new Error("Infinite redirect in navigation guard"))) : B(
            // keep options
            k({
              // preserve an existing replacement but allow the redirect to override it
              replace: O
            }, w(z.to), {
              state: typeof z.to == "object" ? k({}, x, z.to.state) : x,
              force: W
            }),
            // preserve the original redirectedFrom if any
            E || M
          );
      } else
        z = L(M, S, !0, O, x);
      return $(M, S, z), z;
    });
  }
  function Z(p, E) {
    const _ = b(p, E);
    return _ ? Promise.reject(_) : Promise.resolve();
  }
  function ne(p) {
    const E = je.values().next().value;
    return E && typeof E.runWithContext == "function" ? E.runWithContext(p) : p();
  }
  function N(p, E) {
    let _;
    const [S, x, W] = Oi(p, E);
    _ = st(S.reverse(), "beforeRouteLeave", p, E);
    for (const C of S)
      C.leaveGuards.forEach((M) => {
        _.push(ue(M, p, E));
      });
    const O = Z.bind(null, p, E);
    return _.push(O), we(_).then(() => {
      _ = [];
      for (const C of s.list())
        _.push(ue(C, p, E));
      return _.push(O), we(_);
    }).then(() => {
      _ = st(x, "beforeRouteUpdate", p, E);
      for (const C of x)
        C.updateGuards.forEach((M) => {
          _.push(ue(M, p, E));
        });
      return _.push(O), we(_);
    }).then(() => {
      _ = [];
      for (const C of W)
        if (C.beforeEnter)
          if (J(C.beforeEnter))
            for (const M of C.beforeEnter)
              _.push(ue(M, p, E));
          else
            _.push(ue(C.beforeEnter, p, E));
      return _.push(O), we(_);
    }).then(() => (p.matched.forEach((C) => C.enterCallbacks = {}), _ = st(W, "beforeRouteEnter", p, E, ne), _.push(O), we(_))).then(() => {
      _ = [];
      for (const C of i.list())
        _.push(ue(C, p, E));
      return _.push(O), we(_);
    }).catch((C) => re(
      C,
      8
      /* ErrorTypes.NAVIGATION_CANCELLED */
    ) ? C : Promise.reject(C));
  }
  function $(p, E, _) {
    c.list().forEach((S) => ne(() => S(p, E, _)));
  }
  function L(p, E, _, S, x) {
    const W = b(p, E);
    if (W)
      return W;
    const O = E === le, C = oe ? history.state : {};
    _ && (S || O ? o.replace(p.fullPath, k({
      scroll: O && C && C.scroll
    }, x)) : o.push(p.fullPath, x)), u.value = p, jt(p, E, _, O), Xe();
  }
  let Y;
  function Pr() {
    Y || (Y = o.listen((p, E, _) => {
      if (!Lt.listening)
        return;
      const S = y(p), x = F(S);
      if (x) {
        B(k(x, { replace: !0, force: !0 }), S).catch(ke);
        return;
      }
      d = S;
      const W = u.value;
      oe && As(Jt(W.fullPath, _.delta), qe()), N(S, W).catch((O) => re(
        O,
        12
        /* ErrorTypes.NAVIGATION_CANCELLED */
      ) ? O : re(
        O,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? (B(
        k(w(O.to), {
          force: !0
        }),
        S
        // avoid an uncaught rejection, let push call triggerError
      ).then((C) => {
        re(
          C,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && !_.delta && _.type === Re.pop && o.go(-1, !1);
      }).catch(ke), Promise.reject()) : (_.delta && o.go(-_.delta, !1), Ye(O, S, W))).then((O) => {
        O = O || L(
          // after navigation, all matched components are resolved
          S,
          W,
          !1
        ), O && (_.delta && // a new navigation has been triggered, so we do not want to revert, that will change the current history
        // entry while a different route is displayed
        !re(
          O,
          8
          /* ErrorTypes.NAVIGATION_CANCELLED */
        ) ? o.go(-_.delta, !1) : _.type === Re.pop && re(
          O,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && o.go(-1, !1)), $(S, W, O);
      }).catch(ke);
    }));
  }
  let Qe = Ne(), Mt = Ne(), Me;
  function Ye(p, E, _) {
    Xe(p);
    const S = Mt.list();
    return S.length ? S.forEach((x) => x(p, E, _)) : (R.NODE_ENV !== "production" && P("uncaught error during route navigation:"), console.error(p)), Promise.reject(p);
  }
  function Cr() {
    return Me && u.value !== le ? Promise.resolve() : new Promise((p, E) => {
      Qe.add([p, E]);
    });
  }
  function Xe(p) {
    return Me || (Me = !p, Pr(), Qe.list().forEach(([E, _]) => p ? _(p) : E()), Qe.reset()), p;
  }
  function jt(p, E, _, S) {
    const { scrollBehavior: x } = e;
    if (!oe || !x)
      return Promise.resolve();
    const W = !_ && $s(Jt(p.fullPath, 0)) || (S || !_) && history.state && history.state.scroll || null;
    return Se().then(() => x(p, E, W)).then((O) => O && xs(O)).catch((O) => Ye(O, p, E));
  }
  const Ze = (p) => o.go(p);
  let et;
  const je = /* @__PURE__ */ new Set(), Lt = {
    currentRoute: u,
    listening: !0,
    addRoute: h,
    removeRoute: g,
    clearRoutes: t.clearRoutes,
    hasRoute: v,
    getRoutes: m,
    resolve: y,
    options: e,
    push: V,
    replace: A,
    go: Ze,
    back: () => Ze(-1),
    forward: () => Ze(1),
    beforeEach: s.add,
    beforeResolve: i.add,
    afterEach: c.add,
    onError: Mt.add,
    isReady: Cr,
    install(p) {
      const E = this;
      p.component("RouterLink", fi), p.component("RouterView", gi), p.config.globalProperties.$router = E, Object.defineProperty(p.config.globalProperties, "$route", {
        enumerable: !0,
        get: () => U(u)
      }), oe && // used for the initial navigation client side to avoid pushing
      // multiple times when the router is used in multiple apps
      !et && u.value === le && (et = !0, V(o.location).catch((x) => {
        R.NODE_ENV !== "production" && P("Unexpected error when starting the router:", x);
      }));
      const _ = {};
      for (const x in le)
        Object.defineProperty(_, x, {
          get: () => u.value[x],
          enumerable: !0
        });
      p.provide(Je, E), p.provide(Tt, $r(_)), p.provide(Et, u);
      const S = p.unmount;
      je.add(p), p.unmount = function() {
        je.delete(p), je.size < 1 && (d = le, Y && Y(), Y = null, u.value = le, et = !1, Me = !1), S();
      }, R.NODE_ENV !== "production" && oe && yi(p, E, t);
    }
  };
  function we(p) {
    return p.reduce((E, _) => E.then(() => ne(_)), Promise.resolve());
  }
  return Lt;
}
function Oi(e, t) {
  const n = [], r = [], o = [], s = Math.max(t.matched.length, e.matched.length);
  for (let i = 0; i < s; i++) {
    const c = t.matched[i];
    c && (e.matched.find((d) => de(d, c)) ? r.push(c) : n.push(c));
    const u = e.matched[i];
    u && (t.matched.find((d) => de(d, u)) || o.push(u));
  }
  return [n, r, o];
}
function ki() {
  return te(Je);
}
function xi(e) {
  return te(Tt);
}
function Ai(e) {
  const { immediately: t = !1, code: n } = e;
  let r = K(n);
  return t && (r = r()), r;
}
const xe = /* @__PURE__ */ new Map();
function $i(e) {
  if (!xe.has(e)) {
    const t = Symbol();
    return xe.set(e, t), t;
  }
  return xe.get(e);
}
function ye(e, t) {
  var u, d;
  const n = tt(e);
  if (!n)
    return {
      updateVforInfo: () => {
      },
      updateSlotPropValue: () => {
      }
    };
  const { varMap: r, vforRealIndexMap: o } = Ti(n, t);
  if (r.size > 0) {
    const l = $i(e);
    be(l, r);
  }
  Tr(() => {
    r.clear(), o.clear();
  });
  const s = ce({ attached: { varMap: r, sid: e } });
  Ko({
    watchConfigs: n.py_watch || [],
    computedConfigs: n.web_computed || [],
    varMapGetter: s,
    sid: e
  }), (u = n.js_watch) == null || u.forEach((l) => {
    Zo(l, s);
  }), (d = n.vue_watch) == null || d.forEach((l) => {
    Xo(l, s);
  });
  function i(l, a) {
    const f = tt(l);
    if (!f.vfor)
      return;
    const { fi: h, fv: g } = f.vfor;
    h && (r.get(h.id).value = a.index), g && (o.get(g.id).value = a.index);
  }
  function c(l) {
    const { sid: a, value: f } = l;
    if (!a)
      return;
    const h = tt(a), { id: g } = h.sp, m = r.get(g);
    m.value = f;
  }
  return {
    updateVforInfo: i,
    updateSlotPropValue: c
  };
}
function ce(e) {
  const { attached: t, sidCollector: n } = e || {}, [r, o, s] = Di(n);
  t && r.set(t.sid, t.varMap);
  const i = o ? xi() : null, c = s ? ki() : null, u = o ? () => i : () => {
    throw new Error("Route params not found");
  }, d = s ? () => c : () => {
    throw new Error("Router not found");
  };
  function l(m) {
    const v = $e(f(m));
    return Tn(v, m.path ?? [], l);
  }
  function a(m) {
    const v = f(m);
    return xo(v, {
      paths: m.path,
      getBindableValueFn: l
    });
  }
  function f(m) {
    return Wo(m) ? () => u()[m.prop] : r.get(m.sid).get(m.id);
  }
  function h(m, v) {
    if (At(m)) {
      const y = f(m);
      if (m.path) {
        Dn(y.value, m.path, v, l);
        return;
      }
      y.value = v;
      return;
    }
    throw new Error(`Unsupported output binding: ${m}`);
  }
  function g() {
    return d();
  }
  return {
    getValue: l,
    getRouter: g,
    getVueRefObject: a,
    updateValue: h,
    getVueRefObjectWithoutPath: f
  };
}
function cr(e) {
  const t = xe.get(e);
  return te(t);
}
function Ii(e) {
  const t = cr(e);
  if (t === void 0)
    throw new Error(`Scope not found: ${e}`);
  return t;
}
function Ti(e, t) {
  var s, i, c, u, d, l;
  const n = /* @__PURE__ */ new Map(), r = /* @__PURE__ */ new Map(), o = ce({
    attached: { varMap: n, sid: e.id }
  });
  if (e.data && e.data.forEach((a) => {
    n.set(a.id, a.value);
  }), e.jsFn && e.jsFn.forEach((a) => {
    const f = Ai(a);
    n.set(a.id, () => f);
  }), e.vfor) {
    if (!t || !t.initVforInfo)
      throw new Error("Init vfor info not found");
    const { fv: a, fi: f, fk: h } = e.vfor, { index: g, keyValue: m, config: v } = t.initVforInfo;
    if (a) {
      const y = Q(g);
      r.set(a.id, y);
      const { sid: w } = v, b = ts(w), V = fe(() => ({
        get() {
          const A = b.value;
          return Array.isArray(A) ? A[y.value] : Object.values(A)[y.value];
        },
        set(A) {
          const F = b.value;
          if (!Array.isArray(F)) {
            F[m] = A;
            return;
          }
          F[y.value] = A;
        }
      }));
      n.set(a.id, V);
    }
    f && n.set(f.id, Q(g)), h && n.set(h.id, Q(m));
  }
  if (e.sp) {
    const { id: a } = e.sp, f = ((s = t == null ? void 0 : t.initSlotPropInfo) == null ? void 0 : s.value) || null;
    n.set(a, Q(f));
  }
  return (i = e.eRefs) == null || i.forEach((a) => {
    n.set(a.id, Q(null));
  }), (c = e.refs) == null || c.forEach((a) => {
    const f = Do(a);
    n.set(a.id, f);
  }), (u = e.web_computed) == null || u.forEach((a) => {
    const f = jo(a);
    n.set(a.id, f);
  }), (d = e.js_computed) == null || d.forEach((a) => {
    const f = Lo(
      a,
      o
    );
    n.set(a.id, f);
  }), (l = e.vue_computed) == null || l.forEach((a) => {
    const f = Mo(
      a,
      o
    );
    n.set(a.id, f);
  }), { varMap: n, vforRealIndexMap: r };
}
function Di(e) {
  const t = /* @__PURE__ */ new Map();
  if (e) {
    const { sids: n, needRouteParams: r = !0, needRouter: o = !0 } = e;
    for (const s of n)
      t.set(s, Ii(s));
    return [t, r, o];
  }
  for (const n of xe.keys()) {
    const r = cr(n);
    r !== void 0 && t.set(n, r);
  }
  return [t, !0, !0];
}
const Mi = j(ji, {
  props: ["vforConfig", "vforIndex", "vforKeyValue"]
});
function ji(e) {
  const { sid: t, items: n = [] } = e.vforConfig, { updateVforInfo: r } = ye(t, {
    initVforInfo: {
      config: e.vforConfig,
      index: e.vforIndex,
      keyValue: e.vforKeyValue
    }
  });
  return () => (r(t, {
    index: e.vforIndex,
    keyValue: e.vforKeyValue
  }), n.length === 1 ? X(n[0]) : n.map((o) => X(o)));
}
function fn(e) {
  const { start: t = 0, end: n, step: r = 1 } = e;
  let o = [];
  if (r > 0)
    for (let s = t; s < n; s += r)
      o.push(s);
  else
    for (let s = t; s > n; s += r)
      o.push(s);
  return o;
}
const lr = j(Li, {
  props: ["config"]
});
function Li(e) {
  const { fkey: t, tsGroup: n = {} } = e.config, r = ce(), s = Bi(t ?? "index"), i = Hi(e.config, r);
  return es(e.config, i), () => {
    const c = Dr(i.value, (...u) => {
      const d = u[0], l = u[2] !== void 0, a = l ? u[2] : u[1], f = l ? u[1] : a, h = s(d, a);
      return D(Mi, {
        key: h,
        vforIndex: a,
        vforKeyValue: f,
        vforConfig: e.config
      });
    });
    return n && Object.keys(n).length > 0 ? D(yn, n, {
      default: () => c
    }) : c;
  };
}
const Wi = (e) => e, Fi = (e, t) => t;
function Bi(e) {
  const t = bo(e);
  return typeof t == "function" ? t : e === "item" ? Wi : Fi;
}
function Hi(e, t) {
  const { type: n, value: r } = e.array, o = n === pt.range;
  if (n === pt.const || o && typeof r == "number") {
    const i = o ? fn({
      end: Math.max(0, r)
    }) : r;
    return fe(() => ({
      get() {
        return i;
      },
      set() {
        throw new Error("Cannot set value to constant array");
      }
    }));
  }
  if (o) {
    const i = r, c = t.getVueRefObject(i);
    return fe(() => ({
      get() {
        return fn({
          end: Math.max(0, c.value)
        });
      },
      set() {
        throw new Error("Cannot set value to range array");
      }
    }));
  }
  return fe(() => {
    const i = t.getVueRefObject(
      r
    );
    return {
      get() {
        return i.value;
      },
      set(c) {
        i.value = c;
      }
    };
  });
}
const ur = j(zi, {
  props: ["config"]
});
function zi(e) {
  const { sid: t, items: n, on: r } = e.config;
  Ce(t) && ye(t);
  const o = ce();
  return () => (typeof r == "boolean" ? r : o.getValue(r)) ? n.map((i) => X(i)) : void 0;
}
const dn = j(Ui, {
  props: ["slotConfig"]
});
function Ui(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Ce(t) && ye(t), () => n.map((r) => X(r));
}
const it = ":default", fr = j(Gi, {
  props: ["config"]
});
function Gi(e) {
  const { on: t, caseValues: n, slots: r, sid: o } = e.config;
  Ce(o) && ye(o);
  const s = ce();
  return () => {
    const i = s.getValue(t), c = n.map((u, d) => {
      const l = d.toString(), a = r[l];
      return u === i ? D(dn, { slotConfig: a, key: l }) : null;
    }).filter(Boolean);
    return c.length === 0 && it in r ? D(dn, {
      slotConfig: r[it],
      key: it
    }) : c;
  };
}
const Ki = "on:mounted";
function qi(e, t, n) {
  if (!t)
    return e;
  const r = $t(() => []);
  t.map(([c, u]) => {
    const d = Ji(u, n), { eventName: l, handleEvent: a } = ea({
      eventName: c,
      info: u,
      handleEvent: d
    });
    r.getOrDefault(l).push(a);
  });
  const o = {};
  for (const [c, u] of r) {
    const d = u.length === 1 ? u[0] : (...l) => u.forEach((a) => Promise.resolve().then(() => a(...l)));
    o[c] = d;
  }
  const { [Ki]: s, ...i } = o;
  return e = ae(e, i), s && (e = wn(e, [
    [
      {
        mounted(c) {
          s(c);
        }
      }
    ]
  ])), e;
}
function Ji(e, t) {
  if (e.type === "web") {
    const n = Qi(e, t);
    return Yi(e, n, t);
  } else {
    if (e.type === "vue")
      return Zi(e, t);
    if (e.type === "js")
      return Xi(e, t);
  }
  throw new Error(`unknown event type ${e}`);
}
function Qi(e, t) {
  const { inputs: n = [] } = e;
  return (...r) => n.map(({ value: o, type: s }) => {
    if (s === ee.EventContext) {
      const { path: i } = o;
      if (i.startsWith(":")) {
        const c = i.slice(1);
        return K(c)(...r);
      }
      return Po(r[0], i.split("."));
    }
    return s === ee.Ref ? t.getValue(o) : o;
  });
}
function Yi(e, t, n) {
  async function r(...o) {
    const s = t(...o), i = Ln({
      config: e.preSetup,
      varGetter: n
    });
    try {
      i.run();
      const c = await jn().eventSend(e, s);
      if (!c)
        return;
      Ke(c, e.sets, n);
    } finally {
      i.tryReset();
    }
  }
  return r;
}
function Xi(e, t) {
  const { sets: n, code: r, inputs: o = [] } = e, s = K(r);
  function i(...c) {
    const u = o.map(({ value: l, type: a }) => {
      if (a === ee.EventContext) {
        if (l.path.startsWith(":")) {
          const f = l.path.slice(1);
          return K(f)(...c);
        }
        return Ro(c[0], l.path.split("."));
      }
      if (a === ee.Ref) {
        const f = t.getValue(l);
        return kt(f) ? f : Ot(f);
      }
      if (a === ee.Data)
        return l;
      if (a === ee.JsFn)
        return t.getValue(l);
      throw new Error(`unknown input type ${a}`);
    }), d = s(...u);
    if (n !== void 0) {
      const a = n.length === 1 ? [d] : d, f = a.map((h) => h === void 0 ? 1 : 0);
      Ke(
        { values: a, types: f },
        n,
        t
      );
    }
  }
  return i;
}
function Zi(e, t) {
  const { code: n, inputs: r = {} } = e, o = Ge(
    r,
    (c) => c.type !== ee.Data ? t.getVueRefObject(c.value) : c.value
  ), s = K(n, o);
  function i(...c) {
    s(...c);
  }
  return i;
}
function ea(e) {
  const { eventName: t, info: n, handleEvent: r } = e;
  if (n.type === "vue")
    return {
      eventName: t,
      handleEvent: r
    };
  const { modifier: o = [] } = n;
  if (o.length === 0)
    return {
      eventName: t,
      handleEvent: r
    };
  const s = ["passive", "capture", "once"], i = [], c = [];
  for (const l of o)
    s.includes(l) ? i.push(l[0].toUpperCase() + l.slice(1)) : c.push(l);
  const u = i.length > 0 ? t + i.join("") : t, d = c.length > 0 ? Mr(r, c) : r;
  return {
    eventName: u,
    handleEvent: d
  };
}
function ta(e, t) {
  const n = [];
  (e.bStyle || []).forEach((s) => {
    Array.isArray(s) ? n.push(
      ...s.map((i) => t.getValue(i))
    ) : n.push(
      Ge(
        s,
        (i) => t.getValue(i)
      )
    );
  });
  const r = jr([e.style || {}, n]);
  return {
    hasStyle: r && Object.keys(r).length > 0,
    styles: r
  };
}
function dr(e, t) {
  const n = e.classes;
  if (!n)
    return null;
  if (typeof n == "string")
    return at(n);
  const { str: r, map: o, bind: s } = n, i = [];
  return r && i.push(r), o && i.push(
    Ge(
      o,
      (c) => t.getValue(c)
    )
  ), s && i.push(...s.map((c) => t.getValue(c))), at(i);
}
function ze(e, t = !0) {
  if (!(typeof e != "object" || e === null)) {
    if (Array.isArray(e)) {
      t && e.forEach((n) => ze(n, !0));
      return;
    }
    for (const [n, r] of Object.entries(e))
      if (n.startsWith(":"))
        try {
          e[n.slice(1)] = new Function(`return (${r})`)(), delete e[n];
        } catch (o) {
          console.error(
            `Error while converting ${n} attribute to function:`,
            o
          );
        }
      else
        t && ze(r, !0);
  }
}
function na(e, t) {
  const n = e.startsWith(":");
  return n && (e = e.slice(1), t = K(t)), { name: e, value: t, isFunc: n };
}
function ra(e, t, n) {
  var o;
  const r = {};
  return Bt(e.bProps || {}, (s, i) => {
    const c = n.getValue(s);
    ve(c) || (ze(c), r[i] = oa(c, i));
  }), (o = e.proxyProps) == null || o.forEach((s) => {
    const i = n.getValue(s);
    typeof i == "object" && Bt(i, (c, u) => {
      const { name: d, value: l } = na(u, c);
      r[d] = l;
    });
  }), { ...t, ...r };
}
function oa(e, t) {
  return t === "innerText" ? _n(e) : e;
}
const sa = j(ia, {
  props: ["slotPropValue", "config"]
});
function ia(e) {
  const { sid: t, items: n } = e.config, r = Ce(t) ? ye(t, {
    initSlotPropInfo: {
      value: e.slotPropValue
    }
  }).updateSlotPropValue : aa;
  return () => (r({ sid: t, value: e.slotPropValue }), n.map((o) => X(o)));
}
function aa() {
}
function ca(e, t) {
  if (!e.slots)
    return null;
  const n = e.slots ?? {};
  return t ? St(n[":"]) : An(n, { keyFn: (i) => i === ":" ? "default" : i, valueFn: (i) => (c) => i.use_prop ? la(c, i) : St(i) });
}
function la(e, t) {
  return D(sa, { config: t, slotPropValue: e });
}
function ua(e, t, n) {
  const r = [], { dir: o = [] } = t;
  return o.forEach((s) => {
    const { sys: i, name: c, arg: u, value: d, mf: l } = s;
    if (c === "vmodel") {
      const a = n.getVueRefObject(d);
      if (e = ae(e, {
        [`onUpdate:${u}`]: (f) => {
          a.value = f;
        }
      }), i === 1) {
        const f = l ? Object.fromEntries(l.map((h) => [h, !0])) : {};
        r.push([Lr, a.value, void 0, f]);
      } else
        e = ae(e, {
          [u]: a.value
        });
    } else if (c === "vshow") {
      const a = n.getVueRefObject(d);
      r.push([Wr, a.value]);
    } else
      console.warn(`Directive ${c} is not supported yet`);
  }), wn(e, r);
}
function fa(e, t, n) {
  const { eRef: r } = t;
  return r ? ae(e, { ref: n.getVueRefObject(r) }) : e;
}
const hr = Symbol();
function da(e) {
  be(hr, e);
}
function lc() {
  return te(hr);
}
const ha = j(pa, {
  props: ["config"]
});
function pa(e) {
  const { config: t } = e, n = ce({
    sidCollector: new ga(t).getCollectInfo()
  });
  t.varGetterStrategy && da(n);
  const r = t.props ?? {};
  return ze(r, !0), () => {
    const { tag: o } = t, s = typeof o == "string" ? o : n.getValue(o), i = Fr(s), c = typeof i == "string", u = dr(t, n), { styles: d, hasStyle: l } = ta(t, n), a = ca(t, c), f = ra(t, r, n), h = Br(f) || {};
    l && (h.style = d), u && (h.class = u);
    let g = D(i, { ...h }, a);
    return g = qi(g, t.events, n), g = fa(g, t, n), ua(g, t, n);
  };
}
class ga {
  constructor(t) {
    H(this, "sids", /* @__PURE__ */ new Set());
    H(this, "needRouteParams", !0);
    H(this, "needRouter", !0);
    this.config = t;
  }
  /**
   * getCollectFn
   */
  getCollectInfo() {
    const {
      eRef: t,
      dir: n,
      classes: r,
      bProps: o,
      proxyProps: s,
      bStyle: i,
      events: c,
      varGetterStrategy: u
    } = this.config;
    if (u !== "all") {
      if (t && this._tryExtractSidToCollection(t), n && n.forEach((d) => {
        this._tryExtractSidToCollection(d.value), this._extendWithPaths(d.value);
      }), r && typeof r != "string") {
        const { map: d, bind: l } = r;
        d && Object.values(d).forEach((a) => {
          this._tryExtractSidToCollection(a), this._extendWithPaths(a);
        }), l && l.forEach((a) => {
          this._tryExtractSidToCollection(a), this._extendWithPaths(a);
        });
      }
      return o && Object.values(o).forEach((d) => {
        this._tryExtractSidToCollection(d), this._extendWithPaths(d);
      }), s && s.forEach((d) => {
        this._tryExtractSidToCollection(d), this._extendWithPaths(d);
      }), i && i.forEach((d) => {
        Array.isArray(d) ? d.forEach((l) => {
          this._tryExtractSidToCollection(l), this._extendWithPaths(l);
        }) : Object.values(d).forEach((l) => {
          this._tryExtractSidToCollection(l), this._extendWithPaths(l);
        });
      }), c && c.forEach(([d, l]) => {
        this._handleEventInputs(l), this._handleEventSets(l);
      }), Array.isArray(u) && u.forEach((d) => {
        this.sids.add(d.sid);
      }), {
        sids: this.sids,
        needRouteParams: this.needRouteParams,
        needRouter: this.needRouter
      };
    }
  }
  _tryExtractSidToCollection(t) {
    Mn(t) && this.sids.add(t.sid);
  }
  _handleEventInputs(t) {
    if (t.type === "js" || t.type === "web") {
      const { inputs: n } = t;
      n == null || n.forEach((r) => {
        if (r.type === ee.Ref) {
          const o = r.value;
          this._tryExtractSidToCollection(o), this._extendWithPaths(o);
        }
      });
    } else if (t.type === "vue") {
      const { inputs: n } = t;
      if (n) {
        const r = Object.values(n);
        r == null || r.forEach((o) => {
          if (o.type === ee.Ref) {
            const s = o.value;
            this._tryExtractSidToCollection(s), this._extendWithPaths(s);
          }
        });
      }
    }
  }
  _handleEventSets(t) {
    if (t.type === "js" || t.type === "web") {
      const { sets: n } = t;
      n == null || n.forEach((r) => {
        At(r.ref) && (this.sids.add(r.ref.sid), this._extendWithPaths(r.ref));
      });
    }
  }
  _extendWithPaths(t) {
    if (!t.path)
      return;
    const n = [];
    for (n.push(...t.path); n.length > 0; ) {
      const r = n.pop();
      if (r === void 0)
        break;
      if (Oo(r)) {
        const o = ko(r);
        this._tryExtractSidToCollection(o), o.path && n.push(...o.path);
      }
    }
  }
}
const Ae = /* @__PURE__ */ new Map([
  [
    "p",
    {
      classes: "ist-r-p",
      styleVar: "--p",
      handler: (e) => T("space", e)
    }
  ],
  [
    "px",
    {
      classes: "ist-r-px",
      styleVar: "--px",
      handler: (e) => T("space", e)
    }
  ],
  [
    "py",
    {
      classes: "ist-r-py",
      styleVar: "--py",
      handler: (e) => T("space", e)
    }
  ],
  [
    "pt",
    {
      classes: "ist-r-pt",
      styleVar: "--pt",
      handler: (e) => T("space", e)
    }
  ],
  [
    "pb",
    {
      classes: "ist-r-pb",
      styleVar: "--pb",
      handler: (e) => T("space", e)
    }
  ],
  [
    "pl",
    {
      classes: "ist-r-pl",
      styleVar: "--pl",
      handler: (e) => T("space", e)
    }
  ],
  [
    "pr",
    {
      classes: "ist-r-pr",
      styleVar: "--pr",
      handler: (e) => T("space", e)
    }
  ],
  [
    "width",
    {
      classes: "ist-r-w",
      styleVar: "--width",
      handler: (e) => e
    }
  ],
  [
    "height",
    {
      classes: "ist-r-h",
      styleVar: "--height",
      handler: (e) => e
    }
  ],
  [
    "min_width",
    {
      classes: "ist-r-min-w",
      styleVar: "--min_width",
      handler: (e) => e
    }
  ],
  [
    "min_height",
    {
      classes: "ist-r-min-h",
      styleVar: "--min_height",
      handler: (e) => e
    }
  ],
  [
    "max_width",
    {
      classes: "ist-r-max-w",
      styleVar: "--max_width",
      handler: (e) => e
    }
  ],
  [
    "max_height",
    {
      classes: "ist-r-max-h",
      styleVar: "--max_height",
      handler: (e) => e
    }
  ],
  [
    "position",
    {
      classes: "ist-r-position",
      styleVar: "--position",
      handler: (e) => e
    }
  ],
  [
    "inset",
    {
      classes: "ist-r-inset",
      styleVar: "--inset",
      handler: (e) => T("space", e)
    }
  ],
  [
    "top",
    {
      classes: "ist-r-top",
      styleVar: "--top",
      handler: (e) => T("space", e)
    }
  ],
  [
    "right",
    {
      classes: "ist-r-right",
      styleVar: "--right",
      handler: (e) => T("space", e)
    }
  ],
  [
    "bottom",
    {
      classes: "ist-r-bottom",
      styleVar: "--bottom",
      handler: (e) => T("space", e)
    }
  ],
  [
    "left",
    {
      classes: "ist-r-left",
      styleVar: "--left",
      handler: (e) => T("space", e)
    }
  ],
  [
    "overflow",
    {
      classes: "ist-r-overflow",
      styleVar: "--overflow",
      handler: (e) => e
    }
  ],
  [
    "overflow_x",
    {
      classes: "ist-r-ox",
      styleVar: "--overflow_x",
      handler: (e) => e
    }
  ],
  [
    "overflow_y",
    {
      classes: "ist-r-oy",
      styleVar: "--overflow_y",
      handler: (e) => e
    }
  ],
  [
    "flex_basis",
    {
      classes: "ist-r-fb",
      styleVar: "--flex_basis",
      handler: (e) => e
    }
  ],
  [
    "flex_shrink",
    {
      classes: "ist-r-fs",
      styleVar: "--flex_shrink",
      handler: (e) => e
    }
  ],
  [
    "flex_grow",
    {
      classes: "ist-r-fg",
      styleVar: "--flex_grow",
      handler: (e) => e
    }
  ],
  [
    "grid_area",
    {
      classes: "ist-r-ga",
      styleVar: "--grid_area",
      handler: (e) => e
    }
  ],
  [
    "grid_column",
    {
      classes: "ist-r-gc",
      styleVar: "--grid_column",
      handler: (e) => e
    }
  ],
  [
    "grid_column_start",
    {
      classes: "ist-r-gcs",
      styleVar: "--grid_column_start",
      handler: (e) => e
    }
  ],
  [
    "grid_column_end",
    {
      classes: "ist-r-gce",
      styleVar: "--grid_column_end",
      handler: (e) => e
    }
  ],
  [
    "grid_row",
    {
      classes: "ist-r-gr",
      styleVar: "--grid_row",
      handler: (e) => e
    }
  ],
  [
    "grid_row_start",
    {
      classes: "ist-r-grs",
      styleVar: "--grid_row_start",
      handler: (e) => e
    }
  ],
  [
    "grid_row_end",
    {
      classes: "ist-r-gre",
      styleVar: "--grid_row_end",
      handler: (e) => e
    }
  ],
  [
    "m",
    {
      classes: "ist-r-m",
      styleVar: "--m",
      handler: (e) => T("space", e)
    }
  ],
  [
    "mx",
    {
      classes: "ist-r-mx",
      styleVar: "--mx",
      handler: (e) => T("space", e)
    }
  ],
  [
    "my",
    {
      classes: "ist-r-my",
      styleVar: "--my",
      handler: (e) => T("space", e)
    }
  ],
  [
    "mt",
    {
      classes: "ist-r-mt",
      styleVar: "--mt",
      handler: (e) => T("space", e)
    }
  ],
  [
    "mr",
    {
      classes: "ist-r-mr",
      styleVar: "--mr",
      handler: (e) => T("space", e)
    }
  ],
  [
    "mb",
    {
      classes: "ist-r-mb",
      styleVar: "--mb",
      handler: (e) => T("space", e)
    }
  ],
  [
    "ml",
    {
      classes: "ist-r-ml",
      styleVar: "--ml",
      handler: (e) => T("space", e)
    }
  ],
  [
    "display",
    {
      classes: "ist-r-display",
      styleVar: "--display",
      handler: (e) => e
    }
  ],
  [
    "direction",
    {
      classes: "ist-r-fd",
      styleVar: "--direction",
      handler: (e) => e
    }
  ],
  [
    "align",
    {
      classes: "ist-r-ai",
      styleVar: "--align",
      handler: (e) => e
    }
  ],
  [
    "justify",
    {
      classes: "ist-r-jc",
      styleVar: "--justify",
      handler: (e) => e
    }
  ],
  [
    "wrap",
    {
      classes: "ist-r-wrap",
      styleVar: "--wrap",
      handler: (e) => e
    }
  ],
  [
    "gap",
    {
      classes: "ist-r-gap",
      styleVar: "--gap",
      handler: (e) => T("space", e)
    }
  ],
  [
    "gap_x",
    {
      classes: "ist-r-cg",
      styleVar: "--gap_x",
      handler: (e) => T("space", e)
    }
  ],
  [
    "gap_y",
    {
      classes: "ist-r-rg",
      styleVar: "--gap_y",
      handler: (e) => T("space", e)
    }
  ],
  [
    "areas",
    {
      classes: "ist-r-gta",
      styleVar: "--areas",
      handler: (e) => e
    }
  ],
  [
    "columns",
    {
      classes: "ist-r-gtc",
      styleVar: "--columns",
      handler: (e) => hn(e)
    }
  ],
  [
    "rows",
    {
      classes: "ist-r-gtr",
      styleVar: "--rows",
      handler: (e) => hn(e)
    }
  ],
  [
    "flow",
    {
      classes: "ist-r-gaf",
      styleVar: "--flow",
      handler: (e) => e
    }
  ],
  [
    "ctn_size",
    {
      classes: "ist-r-ctn_size",
      styleVar: "--ctn_size",
      handler: (e) => T("container", e)
    }
  ]
]);
function ma(e, t) {
  return I(() => {
    const n = pr(e, t), { as: r = "div", as_child: o = !1 } = n;
    return {
      as: r,
      asChild: o
    };
  });
}
function va(e, t, n, r, o) {
  const { hooks: s, excludeNames: i } = o || {};
  return I(() => {
    var a;
    let {
      classes: c,
      style: u,
      excludeReslut: d
    } = wa(t, n, i);
    return [c, u] = ((a = s == null ? void 0 : s.postProcessClassesHook) == null ? void 0 : a.call(
      s,
      c,
      u,
      t
    )) || [c, u], {
      classes: r ? ya(dr(e, n), c) : c,
      style: u,
      exclude: d
    };
  });
}
function ya(e, t) {
  return e ? `${e} ${t}` : t;
}
function wa(e, t, n) {
  const r = pr(e, t), o = {}, s = [], i = new Set(n || []), c = {
    style: {},
    classesList: []
  };
  for (const [d, l] of Object.entries(r)) {
    if (!Ae.has(d))
      continue;
    const a = typeof l == "object" ? l : { initial: l };
    for (const [f, h] of Object.entries(a)) {
      const { classes: g, styleVar: m, handler: v } = Ae.get(d), y = f === "initial", w = y ? g : `${f}:${g}`, b = y ? m : `${m}-${f}`, V = v(h);
      if (i.has(d)) {
        c.classesList.push(w), c.style[b] = V;
        continue;
      }
      s.push(w), o[b] = V;
    }
  }
  return {
    classes: s.join(" "),
    style: o,
    excludeReslut: c
  };
}
function T(e, t) {
  const n = Number(t);
  if (isNaN(n))
    return t;
  {
    const r = n < 0 ? -1 : 1;
    return `calc(var(--${e}-${n}) * ${r})`;
  }
}
function hn(e) {
  const t = Number(e);
  return isNaN(t) ? e : `repeat(${t}, 1fr)`;
}
function pr(e, t) {
  const n = {};
  for (const [r, o] of Object.entries(e.bind || {})) {
    const s = t.getValue(o);
    ve(s) || (n[r] = s);
  }
  return { ...e.props, ...n };
}
function Dt(e, t) {
  function n(r) {
    const { boxInfo: o, styleInfo: s, item: i } = gr(r, { hooks: t });
    return () => {
      const { as: c, asChild: u } = o.value, { classes: d, style: l } = s.value;
      if (u) {
        const h = X(i);
        return ae(h, { style: l, class: d });
      }
      const a = X({
        ...r.config,
        tag: c,
        // All props have been converted to styleInfo.value , so we don't need to pass them to the element
        props: {
          ...r.config.props,
          _resp: void 0
        }
      }), f = d ? d + " " + e : e;
      return ae(a, { class: f, style: l });
    };
  }
  return n;
}
function _a(e, t) {
  function n(r) {
    const { boxInfo: o, styleInfo: s, item: i } = gr(r, {
      hooks: t,
      excludeNames: ["ctn_size"]
    });
    return () => {
      const { asChild: c } = o.value, u = "div";
      let { classes: d, style: l, exclude: a } = s.value;
      if (c) {
        const m = X(i);
        return ae(m, { style: l, class: d });
      }
      const f = {
        tag: "div",
        classes: ["insta-ContainerInner", ...a.classesList].join(" "),
        slots: r.config.slots
      }, h = X({
        ...r.config,
        tag: u,
        props: {
          ...r.config.props,
          _resp: void 0
        },
        slots: {
          ":": { items: [f] }
        }
      }), g = d ? d + " " + e : e;
      return ae(h, {
        class: g,
        style: { ...l, ...a.style }
      });
    };
  }
  return n;
}
function gr(e, t) {
  var f;
  const { slots: n = {} } = e.config, r = ((f = e.config.props) == null ? void 0 : f._resp) ?? {}, o = n[":"], { sid: s } = o;
  Ce(s) && ye(s);
  const i = ce(), c = ma(r, i), { asChild: u } = c.value, d = o.items;
  if (u && d.length > 1)
    throw new Error("Can only have one child element");
  const l = d[0], a = va(
    l,
    r,
    i,
    u,
    t
  );
  return { boxInfo: c, styleInfo: a, item: l };
}
const Ea = "insta-Box", mr = j(Dt(Ea), {
  props: ["config"]
}), ba = "insta-Flex", vr = j(Dt(ba), {
  props: ["config"]
}), Sa = "insta-Grid", yr = j(
  Dt(Sa, {
    postProcessClassesHook: Va
  }),
  {
    props: ["config"]
  }
);
function Va(e, t) {
  const n = Ae.get("areas").styleVar, r = Ae.get("columns").styleVar, o = n in t, s = r in t;
  if (!o || s)
    return [e, t];
  const i = Ra(t[n]);
  if (i) {
    const { classes: c, styleVar: u } = Ae.get("columns");
    e = `${e} ${c}`, t[u] = i;
  }
  return [e, t];
}
function Ra(e) {
  if (typeof e != "string") return null;
  const t = [...e.matchAll(/"([^"]+)"/g)].map((i) => i[1]);
  if (t.length === 0) return null;
  const o = t[0].trim().split(/\s+/).length;
  return t.every(
    (i) => i.trim().split(/\s+/).length === o
  ) ? `repeat(${o}, 1fr)` : null;
}
const Pa = "insta-Container", wr = j(_a(Pa), {
  props: ["config"]
}), pn = /* @__PURE__ */ new Map([
  [
    "size",
    {
      classes: "ist-r-size",
      handler: (e) => ka(e)
    }
  ],
  [
    "weight",
    {
      classes: "ist-r-weight",
      styleVar: "--weight",
      handler: (e) => e
    }
  ],
  [
    "text_align",
    {
      classes: "ist-r-ta",
      styleVar: "--ta",
      handler: (e) => e
    }
  ],
  [
    "trim",
    {
      classes: (e) => xa("ist-r", e)
    }
  ],
  [
    "truncate",
    {
      classes: "ist-r-truncate"
    }
  ],
  [
    "text_wrap",
    {
      classes: "ist-r-tw",
      handler: (e) => $a(e)
    }
  ],
  [
    "high_contrast",
    {
      classes: "ist-r-high_contrast"
    }
  ],
  [
    "color",
    {
      propHandler: (e) => Aa(e)
    }
  ]
]);
function Ca(e, t) {
  return I(() => {
    const n = _r(e, t), { as: r = "span" } = n;
    return {
      as: r
    };
  });
}
function Na(e, t) {
  return I(() => {
    let {
      classes: n,
      style: r,
      props: o
    } = Oa(e, t);
    return {
      classes: n,
      style: r,
      props: o
    };
  });
}
function Oa(e, t) {
  const n = _r(e, t), r = {}, o = [], s = {};
  for (const [c, u] of Object.entries(n)) {
    if (!pn.has(c))
      continue;
    const d = typeof u == "object" ? u : { initial: u };
    for (const [l, a] of Object.entries(d)) {
      const { classes: f, styleVar: h, handler: g, propHandler: m } = pn.get(c), v = l === "initial";
      if (f) {
        const y = typeof f == "function" ? f(a) : f, w = v ? y : `${l}:${y}`;
        o.push(w);
      }
      if (g) {
        const y = g(a);
        if (h) {
          const w = v ? h : `${h}-${l}`;
          r[w] = y;
        } else {
          if (!Array.isArray(y))
            throw new Error(`Invalid style value: ${y}`);
          y.forEach((w) => {
            for (const [b, V] of Object.entries(w))
              r[b] = V;
          });
        }
      }
      if (m) {
        const y = m(a);
        for (const [w, b] of Object.entries(y))
          s[w] = b;
      }
    }
  }
  return {
    classes: o.join(" "),
    style: r,
    props: s
  };
}
function ka(e) {
  const t = Number(e);
  if (isNaN(t))
    throw new Error(`Invalid font size value: ${e}`);
  return [
    { "--fs": `var(--font-size-${t})` },
    { "--lh": `var(--line-height-${t})` },
    { "--ls": `var(--letter-spacing-${t})` }
  ];
}
function xa(e, t) {
  return `${e}-lt-${t}`;
}
function Aa(e) {
  return {
    "data-accent-color": e
  };
}
function $a(e) {
  if (e === "wrap")
    return {
      "--ws": "normal"
    };
  if (e === "nowrap")
    return {
      "--ws": "nowrap"
    };
  if (e === "pretty")
    return [{ "--ws": "normal" }, { "--tw": "pretty" }];
  if (e === "balance")
    return [{ "--ws": "normal" }, { "--tw": "balance" }];
  throw new Error(`Invalid text wrap value: ${e}`);
}
function _r(e, t) {
  const n = {};
  for (const [r, o] of Object.entries(e.bind || {})) {
    const s = t.getValue(o);
    ve(s) || (n[r] = s);
  }
  return { ...e.props, ...n };
}
function Er(e) {
  function t(n) {
    const { boxInfo: r, styleInfo: o } = Ia(n);
    return () => {
      const { as: s } = r.value, { classes: i, style: c, props: u } = o.value, d = X({
        ...n.config,
        tag: s,
        // All props have been converted to styleInfo.value , so we don't need to pass them to the element
        props: {
          ...n.config.props,
          ...u,
          _resp: void 0
        }
      }), l = i ? i + " " + e : e;
      return ae(d, { class: l, style: c });
    };
  }
  return t;
}
function Ia(e) {
  var s;
  const t = ((s = e.config.props) == null ? void 0 : s._resp) ?? {}, n = ce(), r = Ca(t, n), o = Na(t, n);
  return { boxInfo: r, styleInfo: o };
}
const Ta = "insta-Text", br = j(Er(Ta), {
  props: ["config"]
}), Da = "insta-Heading", Sr = j(Er(Da), {
  props: ["config"]
}), gn = /* @__PURE__ */ new Map([
  ["vfor", (e, t) => D(lr, { config: e, key: t })],
  ["vif", (e, t) => D(ur, { config: e, key: t })],
  ["match", (e, t) => D(fr, { config: e, key: t })],
  ["box", (e, t) => D(mr, { config: e, key: t })],
  ["flex", (e, t) => D(vr, { config: e, key: t })],
  ["grid", (e, t) => D(yr, { config: e, key: t })],
  ["container", (e, t) => D(wr, { config: e, key: t })],
  ["text", (e, t) => D(br, { config: e, key: t })],
  ["heading", (e, t) => D(Sr, { config: e, key: t })]
]);
function X(e, t) {
  const { tag: n } = e;
  return typeof n == "string" && gn.has(n) ? gn.get(n)(e, t) : D(ha, { config: e, key: t });
}
function St(e, t) {
  return D(Vr, { slotConfig: e, key: t });
}
const Vr = j(Ma, {
  props: ["slotConfig"]
});
function Ma(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Ce(t) && ye(t), () => n.map((r) => X(r));
}
function ja(e, t) {
  const { state: n, isReady: r, isLoading: o } = fo(async () => {
    let s = e;
    const i = t;
    if (!s && !i)
      throw new Error("Either config or configUrl must be provided");
    if (!s && i && (s = await (await fetch(i)).json()), !s)
      throw new Error("Failed to load config");
    return s;
  }, {});
  return { config: n, isReady: r, isLoading: o };
}
function La(e) {
  const t = G(!1), n = G("");
  function r(o, s) {
    let i;
    return s.component ? i = `Error captured from component:tag: ${s.component.tag} ; id: ${s.component.id} ` : i = "Error captured from app init", console.group(i), console.error("Component:", s.component), console.error("Error:", o), console.groupEnd(), e && (t.value = !0, n.value = `${i} ${o.message}`), !1;
  }
  return Hr(r), { hasError: t, errorMessage: n };
}
let Vt;
function Wa(e) {
  if (e === "web" || e === "webview") {
    Vt = Fa;
    return;
  }
  if (e === "zero") {
    Vt = Ba;
    return;
  }
  throw new Error(`Unsupported mode: ${e}`);
}
function Fa(e) {
  const { assetPath: t = "/assets/icons", icon: n = "" } = e, [r, o] = n.split(":");
  return {
    assetPath: t,
    svgName: `${r}.svg`
  };
}
function Ba() {
  return {
    assetPath: "",
    svgName: ""
  };
}
function Ha(e, t) {
  const n = I(() => {
    const r = e.value;
    if (!r)
      return null;
    const i = new DOMParser().parseFromString(r, "image/svg+xml").querySelector("svg");
    if (!i)
      throw new Error("Invalid svg string");
    const c = {};
    for (const f of i.attributes)
      c[f.name] = f.value;
    const { size: u, color: d, attrs: l } = t;
    d.value !== null && d.value !== void 0 && (i.removeAttribute("fill"), i.querySelectorAll("*").forEach((h) => {
      h.hasAttribute("fill") && h.setAttribute("fill", "currentColor");
    }), c.color = d.value), u.value !== null && u.value !== void 0 && (c.width = u.value.toString(), c.height = u.value.toString());
    const a = i.innerHTML;
    return {
      ...c,
      ...l,
      innerHTML: a
    };
  });
  return () => {
    if (!n.value)
      return null;
    const r = n.value;
    return D("svg", r);
  };
}
const za = {
  class: "app-box insta-theme",
  "data-accent-color": "teal",
  "data-scaling": "100%"
}, Ua = {
  key: 0,
  style: { position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)" }
}, Ga = {
  key: 0,
  style: { color: "red", "font-size": "1.2em", margin: "1rem", border: "1px dashed red", padding: "1rem" }
}, Ka = /* @__PURE__ */ j({
  __name: "App",
  props: {
    config: {},
    meta: {},
    configUrl: {}
  },
  setup(e) {
    const t = e, { debug: n = !1 } = t.meta, { config: r, isLoading: o } = ja(
      t.config,
      t.configUrl
    );
    q(r, (c) => {
      c.url && (Qr({
        mode: t.meta.mode,
        version: t.meta.version,
        queryPath: c.url.path,
        pathParams: c.url.params,
        webServerInfo: c.webInfo
      }), zo(t.meta.mode)), Wa(t.meta.mode), Yr(c);
    });
    const { hasError: s, errorMessage: i } = La(n);
    return (c, u) => (ie(), ge("div", za, [
      U(o) ? (ie(), ge("div", Ua, u[0] || (u[0] = [
        En("p", { style: { margin: "auto" } }, "Loading ...", -1)
      ]))) : (ie(), ge("div", {
        key: 1,
        class: at(["insta-main", U(r).class])
      }, [
        zr(U(Vr), { "slot-config": U(r) }, null, 8, ["slot-config"]),
        U(s) ? (ie(), ge("div", Ga, _n(U(i)), 1)) : ct("", !0)
      ], 2))
    ]));
  }
});
function qa(e, { slots: t }) {
  const { name: n = "fade", tag: r } = e;
  return () => D(
    yn,
    { name: n, tag: r },
    {
      default: t.default
    }
  );
}
const Ja = j(qa, {
  props: ["name", "tag"]
});
function Qa(e) {
  const { content: t, r: n = 0 } = e, r = ce(), o = n === 1 ? () => r.getValue(t) : () => t;
  return () => Ur(o());
}
const Ya = j(Qa, {
  props: ["content", "r"]
}), Xa = /* @__PURE__ */ j({
  __name: "_Teleport",
  props: {
    to: {},
    defer: { type: Boolean, default: !0 },
    disabled: { type: Boolean, default: !1 }
  },
  setup(e) {
    return (t, n) => (ie(), bn(Gr, {
      to: t.to,
      defer: t.defer,
      disabled: t.disabled
    }, [
      Sn(t.$slots, "default")
    ], 8, ["to", "defer", "disabled"]));
  }
}), Za = ["width", "height", "color"], ec = ["xlink:href"], tc = /* @__PURE__ */ j({
  __name: "Icon",
  props: {
    size: {},
    icon: {},
    color: {},
    assetPath: {},
    svgName: {},
    rawSvg: {}
  },
  setup(e) {
    const t = e, { assetPath: n, svgName: r } = Vt(t), o = pe(() => t.icon ? t.icon.split(":")[1] : ""), s = pe(() => t.size || "1em"), i = pe(() => t.color || "currentColor"), c = pe(() => t.rawSvg || null), u = I(() => `${n}/${r}/#${o.value}`), d = Kr(), l = Ha(c, {
      size: pe(() => t.size),
      color: pe(() => t.color),
      attrs: d
    });
    return (a, f) => (ie(), ge(Vn, null, [
      o.value ? (ie(), ge("svg", qr({
        key: 0,
        width: s.value,
        height: s.value,
        color: i.value
      }, U(d)), [
        En("use", { "xlink:href": u.value }, null, 8, ec)
      ], 16, Za)) : ct("", !0),
      c.value ? (ie(), bn(U(l), { key: 1 })) : ct("", !0)
    ], 64));
  }
}), nc = ["data-accent-color"], rc = /* @__PURE__ */ j({
  __name: "Theme",
  props: {
    accentColor: {}
  },
  setup(e) {
    return (t, n) => (ie(), ge("div", {
      class: "insta-theme",
      "data-accent-color": t.accentColor
    }, [
      Sn(t.$slots, "default")
    ], 8, nc));
  }
});
function oc(e) {
  if (!e.router)
    throw new Error("Router config is not provided.");
  const { routes: t, kAlive: n = !1 } = e.router;
  return t.map(
    (o) => Rr(o, n)
  );
}
function Rr(e, t) {
  var c;
  const { server: n = !1, vueItem: r } = e, o = () => {
    if (n)
      throw new Error("Server-side rendering is not supported yet.");
    return Promise.resolve(sc(e, t));
  }, s = (c = r.children) == null ? void 0 : c.map(
    (u) => Rr(u, t)
  ), i = {
    ...r,
    children: s,
    component: o
  };
  return r.component.length === 0 && delete i.component, s === void 0 && delete i.children, i;
}
function sc(e, t) {
  const { sid: n, vueItem: r } = e, { path: o, component: s } = r, i = St(
    {
      items: s,
      sid: n
    },
    o
  ), c = D(Vn, null, i);
  return t ? D(Jr, null, () => i) : c;
}
function ic(e, t) {
  const { mode: n = "hash" } = t.router, r = n === "hash" ? js() : n === "memory" ? Ms() : Yn();
  e.use(
    Ni({
      history: r,
      routes: oc(t)
    })
  );
}
function uc(e, t) {
  e.component("insta-ui", Ka), e.component("vif", ur), e.component("vfor", lr), e.component("match", fr), e.component("teleport", Xa), e.component("icon", tc), e.component("ts-group", Ja), e.component("content", Ya), e.component("heading", Sr), e.component("box", mr), e.component("flex", vr), e.component("grid", yr), e.component("container", wr), e.component("text", br), e.component("theme", rc), t.router && ic(e, t);
}
export {
  ze as convertDynamicProperties,
  uc as install,
  lc as useVarGetter
};
//# sourceMappingURL=insta-ui.js.map
