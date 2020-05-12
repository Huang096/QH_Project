export function chemicalFormula(formula, charge) {
  if (formula === null || formula === undefined) {
    return '';
  }
  let form = formula.replace(/([0-9])/g, '<sub>$1</sub>');
  if (charge) {
    form = `${form}<sup>${Math.abs(charge) !== 1 ? Math.abs(charge) : ''}${charge > 0 ? '+' : '-'}</sup>`;
  }
  return form;
}

export function chemicalName(value) {
  if (value === null || value === undefined) {
    return '';
  }
  return value.replace(/([^\s])(\+)([^\s]?)/g, '$1<sup class="top">+</sup>$3')
    .replace(/H2O/g, 'H<sub>2</sub>O').replace(/(O|H)(2|3)(-?)/g, '$1<sub>$2$3</sub>');
}

export function chemicalNameExternalLink(value, link) {
  if (value === null || value === undefined) {
    return '';
  }

  if (link === null) {
    return chemicalName(value);
  }

  return `<a
            target='_blank'
            href='${link}'
          >${chemicalName(value)}</a>`;
}

function chemicalReactionSign(value, reversible) {
  if (value === null) {
    return '';
  }
  // apply chemical name to all metabolites
  if (reversible) {
    return chemicalName(value).replace(/(=>)/g, '&#8660;');
  }
  return chemicalName(value).replace(/(=>)/g, '&#8680;');
}

export function chemicalReaction(value, r) {
  if (typeof r !== 'boolean' && 'is_reversible' in r) {
    return chemicalReactionSign(value, r.is_reversible);
  }
  return chemicalReactionSign(value, r);
}
