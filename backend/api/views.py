from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from itertools import chain
from rest_framework import permissions
from django.conf import settings
import api.models as APImodels
import api.serializers as APIserializer
import api.serializers_rc as APIrcSerializer
from functools import reduce

import requests
import re
import logging
import functools

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def is_model_valid(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        model = kwargs.get('model')
        if not model:
            model = args.get('model')
        try:
            m = APImodels.GEM.objects.get(database_name=model)
        except APImodels.GEM.DoesNotExist:
            return HttpResponse("Invalid model name '%s'" % model, status=404)
        return view_func(request, *args, **kwargs)
    return wrapper


class IsModelValid(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            APImodels.GEM.objects.get(database_name=request.model)
        except APImodels.GEM.DoesNotExist:
            return False
        return True


def componentDBserializerSelector(database, type, serializer_type=None, api_version=None):
    serializer_choice = ['basic', 'lite', 'table', 'search', None]
    if serializer_type not in serializer_choice:
        raise ValueError("Error serializer type, choices are %s" % ", ".join([str(e) for e in serializer_choice]))

    if database in ['hmr2', 'hmr2n', 'hmr3']:
        if type == 'reaction component':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.ReactionComponentLiteSerializer
            return APIrcSerializer.HmrReactionComponentSerializer
        elif type == 'metabolite':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.HmrMetaboliteReactionComponentLiteSerializer
            if serializer_type in ['search']:
                return APIrcSerializer.MetaboliteReactionComponentSearchSerializer
            return APIrcSerializer.HmrMetaboliteReactionComponentSerializer
        elif type == 'enzyme':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.HmrEnzymeReactionComponentLiteSerializer
            elif serializer_type in ['search']:
                return APIrcSerializer.EnzymeReactionComponentSearchSerializer
            return APIrcSerializer.HmrEnzymeReactionComponentSerializer
        elif type == 'reaction':
            if serializer_type == 'basic':
                return APIserializer.HmrReactionBasicSerializer
            if serializer_type == 'lite':
                return APIserializer.HmrReactionLiteSerializer
            if serializer_type == 'table':
                return APIserializer.HmrReactionBasicRTSerializer
            if serializer_type == 'search':
                return APIserializer.ReactionSearchSerializer
            return APIserializer.HmrReactionSerializer
        elif type == 'subsystem':
            if serializer_type == 'lite':
                return APIserializer.SubsystemLiteSerializer
            elif serializer_type == 'search':
                return APIserializer.SubsystemSearchSerializer
            return APIserializer.HmrSubsystemSerializer
        elif type == 'interaction partner':
            if serializer_type == 'lite':
                return APIserializer.HmrInteractionPartnerLiteSerializer
            return APIserializer.HmrInteractionPartnerSerializer
    else:
        if type == 'reaction component':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.ReactionComponentLiteSerializer
            return APIrcSerializer.ReactionComponentSerializer
        elif type == 'metabolite':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.ReactionComponentSerializer
            elif serializer_type in ['search']:
                return APIrcSerializer.MetaboliteReactionComponentSearchSerializer
            return APIrcSerializer.MetaboliteReactionComponentSerializer
        elif type == 'enzyme':
            if serializer_type in ['lite', 'basic']:
                return APIrcSerializer.ReactionComponentSerializer
            if serializer_type in ['search']:
                return APIrcSerializer.EnzymeReactionComponentSearchSerializer
            return APIrcSerializer.EnzymeReactionComponentSerializer
        elif type == 'reaction':
            if serializer_type == 'basic':
                return APIserializer.ReactionBasicSerializer    
            if serializer_type == 'lite':
                return APIserializer.ReactionLiteSerializer
            if serializer_type == 'table':
                return APIserializer.HmrReactionBasicRTSerializer
            if serializer_type == 'search':
                return APIserializer.ReactionSearchSerializer
            return APIserializer.ReactionSerializer
        elif type == 'subsystem':
            if serializer_type == 'lite':
                return APIserializer.SubsystemLiteSerializer
            elif serializer_type =='search':
                return APIserializer.SubsystemSearchSerializer
            return APIserializer.SubsystemSerializer
        elif type == 'interaction partner':
            if serializer_type == 'lite':
                return APIserializer.InteractionPartnerLiteSerializer
            return APIserializer.InteractionPartnerSerializer



@api_view()
@is_model_valid
def get_reactions(request, model):
    """
    Returns all reactions for the given model
    """
    limit = int(request.query_params.get('limit', 10000))
    offset = int(request.query_params.get('offset', 0))
    reactions = APImodels.Reaction.objects.using(model).all()[offset:(offset+limit)]

    serializerClass = componentDBserializerSelector(model, 'reaction', serializer_type="basic", api_version=request.version)

    serializer = serializerClass(reactions, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_reaction(request, model, id):
    """
    Returns all the information we have about a reaction (for example HMR_3905).
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    ReactionSerializerClass = componentDBserializerSelector(model, 'reaction', serializer_type='lite', api_version=request.version)
    reactionserializer = ReactionSerializerClass(reaction, context={'model': model})

    # TODO move that in the javascript
    pmids = APImodels.ReactionReference.objects.using(model).filter(reaction_id=id)
    if pmids.count():
        pmidserializer = APIserializer.ReactionReferenceSerializer(pmids, many=True)
        url = ('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
               '?db=pubmed&retmode=json&id={}'.format(
                   ','.join([x['pmid'].replace('PMID:', '')
                             for x in pmidserializer.data])))
        pmidsresponse = requests.get(url).json()['result']
    else:
        pmidsresponse = {}

    return JSONResponse({'reaction': reactionserializer.data,
                         'pmids': pmidsresponse})


@api_view()
@is_model_valid
def get_reaction_reactants(request, model, id):
    """
    For a given reaction returns all the metabolites that are consumed.
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).prefetch_related('reactants__metabolite').get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    ReactantsSerializerClass = componentDBserializerSelector(model, 'metabolite', serializer_type='lite', api_version=request.version)
    serializer = ReactantsSerializerClass(reaction.reactants, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_reaction_products(request, model, id):
    """
    For a given reaction show the metabolites that are produced.
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).prefetch_related('products__metabolite').get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    ProductsSerializerClass = componentDBserializerSelector(model, 'metabolite', serializer_type='lite', api_version=request.version)
    serializer = ProductsSerializerClass(reaction.products, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_reaction_modifiers(request, model, id):
    """
    For a given reaction returns the proteins that are modifying it.
    """
    try:
        reaction = APImodels.Reaction.objects.using(model).prefetch_related('modifiers__enzyme').get(id__iexact=id)
    except APImodels.Reaction.DoesNotExist:
        return HttpResponse(status=404)

    EnzymesSerializerClass = componentDBserializerSelector(model, 'enzyme', serializer_type='lite', api_version=request.version)
    serializer = EnzymesSerializerClass(reaction.modifiers, many=True, context={'model': model})
    return JSONResponse(serializer.data)


@api_view()
def get_metabolite_interaction_partners(request, model, id):
    """
        For a given metabolite, pull out all first order interaction partners.
    """
    response = get_interaction_partners(request=request._request, model=model, id=id, type='m')
    return response


@api_view()
def get_enzyme_interaction_partners(request, model, id):
    """
        For a given enzyme, pull out all first order interaction partners.
    """
    response = get_interaction_partners(request=request._request, model=model, id=id, type='e')
    return response


@api_view()
@is_model_valid
def get_interaction_partners(request, model, id, type=None):
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(id__iexact=id)
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    reactions = []
    if type == 'm':
        reactions = component.reactions_as_metabolite.prefetch_related('reactants', 'products', 'modifiers').all()
    elif type == 'e':
        reactions = component.reactions_as_modifier.prefetch_related('reactants', 'products', 'modifiers').all()

    InteractionPartnerSerializerClass = componentDBserializerSelector(model, 'interaction partner', serializer_type="lite", api_version=request.version)
    serializer = InteractionPartnerSerializerClass(reactions, many=True)
    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_enzymes(request, model):
    """
    List enzymes in the given model
    """
    limit = int(request.query_params.get('limit', 10000))
    offset = int(request.query_params.get('offset', 0))

    enzymes = APImodels.ReactionComponent.objects.using(model).filter(component_type='e').select_related('enzyme')[offset:(offset+limit)]

    EnzymeSerializerClass = componentDBserializerSelector(model, 'enzyme', api_version=request.version)
    serializer = EnzymeSerializerClass(enzymes, many=True, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_enzyme(request, model, id):
    """
    Return all information for a given enzyme (for example ENSG00000196502 or SULTA1).
    """
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(Q(id__iexact=id) |
                                                                         Q(name__iexact=id))
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    if component.component_type == 'm':
        return HttpResponse(status=404)

    serializerClass = componentDBserializerSelector(model, 'enzyme', api_version=request.version)
    serializer = serializerClass(component, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_metabolites(request, model):
    """
    List metabolites in the given model
    """
    limit = int(request.query_params.get('limit', 10000))
    offset = int(request.query_params.get('offset', 0))

    enzymes = APImodels.ReactionComponent.objects.using(model).filter(component_type='m').select_related('metabolite')[offset:(offset+limit)]

    MetaboliteSerializerClass = componentDBserializerSelector(model, 'metabolite', api_version=request.version)
    serializer = MetaboliteSerializerClass(enzymes, many=True, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_metabolite(request, model, id):
    """
        Return all information for a given metabolite (for example m01587m or citrate[m]).
    """
    try:
        component = APImodels.ReactionComponent.objects.using(model).get(Q(id__iexact=id) |
                                                                         Q(full_name__iexact=id))
    except APImodels.ReactionComponent.DoesNotExist:
        return HttpResponse(status=404)

    if component.component_type == 'e':
        return HttpResponse(status=404)

    serializerClass = componentDBserializerSelector(model, 'metabolite', api_version=request.version)
    serializer = serializerClass(component, context={'model': model})

    return JSONResponse(serializer.data)



@api_view()
@is_model_valid
def get_metabolite_reactions(request, model, id, all_compartment=False):
    """
        list in which reactions does a given metabolite occur,
        supply a metabolite ID or its name (for example m02439c or malate).
    """
    component = APImodels.ReactionComponent.objects.using(model).filter((Q(id__iexact=id) |
                                                                         Q(full_name__iexact=id)) &
                                                                         Q(component_type='m'))
    if not component:
        return HttpResponse(status=404)

    if all_compartment:
        component = APImodels.ReactionComponent.objects.using(model).filter(Q(name=component[0].name) &
                                                                                Q(component_type='m'))

    reactions = APImodels.Reaction.objects.none()
    for c in component:
        reactions_as_met = c.reactions_as_metabolite.using(model). \
            prefetch_related('reactants', 'products', 'modifiers').distinct()
        # reactions_as_products = c.reactions_as_product.using(model). \
        # prefetch_related('reactants', 'products', 'modifiers').distinct()
        reactions |= reactions_as_met
    
    reactions = reactions.distinct()
    ReactionSerializerClass= componentDBserializerSelector(model, 'reaction', serializer_type='table', api_version=request.version)
    serializer = ReactionSerializerClass(reactions[:200], many=True, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_enzyme_reactions(request, model, id):
    """
        list in which reactions does a given enzyme occur,
        supply a enzyme/gene ID or its name (for example ENSG00000180011).
    """
    component = APImodels.ReactionComponent.objects.using(model).filter((Q(id__iexact=id) |
                                                                         Q(name__iexact=id)) &
                                                                         Q(component_type='e'))

    if not component:
        return HttpResponse(status=404)

    reactions = APImodels.Reaction.objects.none()
    for c in component:
        reactions_as_modifier = c.reactions_as_modifier.using(model). \
        prefetch_related('reactants', 'products', 'modifiers').distinct()
        reactions |= reactions_as_modifier

    reactions = reactions.distinct()
    ReactionSerializerClass= componentDBserializerSelector(model, 'reaction', serializer_type='table', api_version=request.version)
    serializer = ReactionSerializerClass(reactions[:200], many=True, context={'model': model})

    return JSONResponse(serializer.data)


def rewriteEquation(term):
    # TODO there is probably something better to do here
    # fix compartment letter size
    term = term.replace("+", " + ")
    term = term.replace("=>", " => ")
    term = re.sub("\\s{2,}", " ", term)
    term = term.strip()
    term = re.sub("(NA|NADP|H)\s\+\s\[", "\g<1>+[", term, flags=re.IGNORECASE)
    term = re.sub("(NA|NADP|H)\s\+(\s=>|$)", "\g<1>+\g<2>", term, flags=re.IGNORECASE)
    rp = term.split('=>')
    if len(rp) > 1:
        reactants = rp[0].split(' + ')
        for i in range(len(reactants)):
            reactants[i] = reactants[i].strip()
            if reactants[i] and not re.match(".+\[.\]$", reactants[i]):
                reactants[i] = reactants[i] + "[_]"
        products = rp[1].split(' + ')
        for i in range(len(products)):
            products[i] = products[i].strip()
            if products[i] and not re.match(".+\[.\]$", products[i]):
                products[i] = products[i] + "[_]"
        reactants = " + ".join(reactants)
        products = " + ".join(products)
        return "%%%s => %s%%" % (reactants, products)
    else:
        elements = rp[0].split(' + ')
        for i in range(len(elements)):
            elements[i] = elements[i].strip()
            if elements[i] and not re.match(".+\[.\]$", elements[i]):
                elements[i] = elements[i] + "[_]"

        elements = " + ".join(elements)
        return "%%%s%%" % elements


@api_view()
def search(request, model, term):
    """
        Searches for the term in metabolites, enzymes, reactions, subsystems and compartments.
        Current search rules:
        
        =: exact match, case insensitive
        ~: contain in, case insensitive

        compartment:
            ~name
        subsystem:
            ~name
            =external_id
        reaction:
            =id
            ~name
            ~equation
            ~name_equation
            ~ec
            =sbo
        metabolite:
            =id
            ~full_name
            ~alt_name1
            ~alt_name2
            ~aliases
            =external_id1
            =external_id2
            =external_id3
            =external_id4
            ~formula
        enzyme:
            same as metabolite, but name instead of full_name
    """

    # l = logging.getLogger('django.db.backends')
    # l.setLevel(logging.DEBUG)
    # l.addHandler(logging.StreamHandler())

    term = term.replace(";", "#") # to avoid match list of aliases
    term = term.strip()

    if len(term) < 2:
        return HttpResponse("Invalid query, term must be at least 2 characters long", status=400)

    results = {}
    models_dict = {}
    quickSearch = model != 'all'
    if not quickSearch:
        models = [k for k in settings.DATABASES if k not in ['default', 'gems']]
        limit = 10000
    else:
        try:
            m = APImodels.GEM.objects.get(database_name=model)
        except APImodels.GEM.DoesNotExist:
            return HttpResponse("Invalid model name '%s'" % model, status=404)
        models = [model]
        limit = 50

    for model_db_name in models:
        m = APImodels.GEM.objects.get(database_name=model_db_name)
        models_dict[model_db_name] = m.short_name

    match_found = False
    for model in models:
        if model not in results:
            results[model] = {}

        m = APImodels.GEM.objects.get(database_name=model)
        model_short_name = m.short_name

        term = term.replace("→", "=>")
        term = term.replace("⇒", "=>")
        term = term.replace("⇔", "=>")
        term = term.replace("->", "=>")

        reactions = APImodels.Reaction.objects.using(model).none()
        metabolites = APImodels.ReactionComponent.objects.using(model).none()
        enzymes = APImodels.ReactionComponent.objects.using(model).none()
        compartments = APImodels.Compartment.objects.using(model).none()
        subsystems = APImodels.Subsystem.objects.using(model).none()

        if '=>' in term and term.count('=>') == 1:
            if not term.strip() == '=>':
                reactants, products = term.split('=>')
                reactants_mets_terms = [rm.strip() for rm in reactants.split(" + ") if rm.strip()]
                reactants = APImodels.ReactionComponent.objects.using(model).filter(
                    Q(component_type__exact='m') &
                    (reduce(lambda x, y: x | y, [Q(id__iexact=w) for w in reactants_mets_terms]) |
                    reduce(lambda x, y: x | y, [Q(name__iexact=w) for w in reactants_mets_terms]) |
                    reduce(lambda x, y: x | y, [Q(full_name__iexact=w) for w in reactants_mets_terms]))
                )[:limit]
                # convert into dicts of list
                dr = {}
                for m in reactants:
                    if m.name not in dr:
                        dr[m.name] = []
                    dr[m.name].append(m.id)

                products_mets_terms = [pm.strip() for pm in products.split(" + ") if pm.strip()]
                products = APImodels.ReactionComponent.objects.using(model).filter(
                    Q(component_type__exact='m') &
                    (reduce(lambda x, y: x | y, [Q(id__iexact=w) for w in products_mets_terms]) |
                    reduce(lambda x, y: x | y, [Q(name__iexact=w) for w in products_mets_terms]) |
                    reduce(lambda x, y: x | y, [Q(full_name__iexact=w) for w in products_mets_terms]))
                )[:limit]
                # convert into dicts of list
                dp = {}
                for m in products:
                    if m.name not in dp:
                        dp[m.name] = []
                    dp[m.name].append(m.id)

                if len(dr) == len(reactants_mets_terms) and len(dp) == len(products_mets_terms):
                    reactions = APImodels.Reaction.objects.using(model) \
                    .prefetch_related('subsystem').filter(
                        reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionReactant.objects.filter(reactant_id__in=l) \
                            .values_list('reaction_id', flat=True)) for l in dr.values()]), \
                        reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionProduct.objects.filter(product_id__in=l) \
                            .values_list('reaction_id', flat=True)) for l in dp.values()]), \
                        )
        elif " + " in term:
            mets_terms = [m.strip() for m in term.split(" + ") if m.strip()]
            mets = APImodels.ReactionComponent.objects.using(model).filter(
                Q(component_type__exact='m') &
                (reduce(lambda x, y: x | y, [Q(id__iexact=w) for w in mets_terms]) |
                reduce(lambda x, y: x | y, [Q(name__iexact=w) for w in mets_terms]) |
                reduce(lambda x, y: x | y, [Q(full_name__iexact=w) for w in mets_terms]))
            ).distinct()[:limit]
            d = {}
            for m in mets:
                if m.name not in d:
                    d[m.name] = []
                d[m.name].append(m.id)

            if len(d) == len(mets_terms):
                reactions = APImodels.Reaction.objects.using(model).filter(
                    reduce(lambda x, y: x & y, [Q(id__in=APImodels.ReactionMetabolite.objects.filter(rc_id__in=l).values_list('reaction_id', flat=True)) \
                     for l in d.values()])).prefetch_related('subsystem')

        else:
            compartments = APImodels.Compartment.objects.using(model).filter(name__icontains=term)

            subsystems = APImodels.Subsystem.objects.using(model).prefetch_related('compartment').filter(
                Q(name__icontains=term) |
                Q(external_id__iexact=term)
            )

            metabolites = APImodels.ReactionComponent.objects.using(model).select_related('metabolite').prefetch_related('subsystem_metabolite').filter(
                Q(component_type__exact='m') &
                (Q(id__iexact=term) |
                Q(full_name__icontains=term) |
                Q(alt_name1__icontains=term) |
                Q(alt_name2__icontains=term) |
                Q(aliases__icontains=term) |
                Q(external_id1__iexact=term) |
                Q(external_id2__iexact=term) |
                Q(external_id3__iexact=term) |
                Q(external_id4__iexact=term) |
                Q(formula__icontains=term))
            )[:limit]

            reactions = APImodels.Reaction.objects.using(model).prefetch_related('subsystem').filter(Q(metabolites__in=metabolites))
            reactions |= APImodels.Reaction.objects.using(model).prefetch_related('subsystem').filter(
                Q(id__iexact=term) |
                Q(name__icontains=term) |
                Q(ec__icontains=term) |
                Q(sbo_id__iexact=term) |
                Q(external_id1__iexact=term) |
                Q(external_id2__iexact=term) |
                Q(external_id3__iexact=term) |
                Q(external_id4__iexact=term)
            )[:limit]
            reactions = reactions.distinct()

            enzymes = APImodels.ReactionComponent.objects.using(model).select_related('enzyme').prefetch_related('subsystem_enzyme', 'compartments').filter(
                Q(component_type__exact='e') &
                (Q(id__iexact=term) |
                Q(name__icontains=term) |
                Q(alt_name1__icontains=term) |
                Q(alt_name2__icontains=term) |
                Q(aliases__icontains=term) |
                Q(external_id1__iexact=term) |
                Q(external_id2__iexact=term) |
                Q(external_id3__iexact=term) |
                Q(external_id4__iexact=term))
            )[:limit]

        if (metabolites.count() + enzymes.count() + compartments.count() + subsystems.count() + reactions.count()) != 0:
            match_found = True

        MetaboliteSerializerClass = componentDBserializerSelector(model, 'metabolite', serializer_type='lite' if quickSearch else 'search', api_version=request.version)
        EnzymeSerializerClass = componentDBserializerSelector(model, 'enzyme', serializer_type='lite' if quickSearch else 'search', api_version=request.version)
        ReactionSerializerClass= componentDBserializerSelector(model, 'reaction', serializer_type='basic' if quickSearch else 'search', api_version=request.version)
        SubsystemSerializerClass = componentDBserializerSelector(model, 'subsystem', serializer_type='lite' if quickSearch else 'search', api_version=request.version)

        metaboliteSerializer = MetaboliteSerializerClass(metabolites, many=True)
        enzymeSerializer = EnzymeSerializerClass(enzymes, many=True)
        compartmentSerializer = APIserializer.CompartmentSerializer(compartments, many=True)
        subsystemSerializer = SubsystemSerializerClass(subsystems, many=True, context={'model': model})
        reactionSerializer = ReactionSerializerClass(reactions, many=True, context={'model': model})

        results[model]['metabolite'] = metaboliteSerializer.data
        results[model]['enzyme'] = enzymeSerializer.data
        results[model]['compartment'] = compartmentSerializer.data
        results[model]['subsystem'] = subsystemSerializer.data
        results[model]['reaction'] = reactionSerializer.data
        results[model]['name'] = model_short_name

        response = JSONResponse(results)

    if not match_found:
        return HttpResponse(status=404)

    return response


@api_view()
@is_model_valid
def get_subsystem(request, model, subsystem_name_id):
    """
        For a given subsystem name, get all containing metabolites, enzymes, and reactions.
    """
    try:
        subsystem = APImodels.Subsystem.objects.using(model).get(Q(name_id__iexact=subsystem_name_id) | Q(name__iexact=subsystem_name_id))
        subsystem_id = subsystem.id
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    try:
        s = APImodels.Subsystem.objects.using(model).get(id=subsystem_id)
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)


    smsQuerySet = APImodels.SubsystemMetabolite.objects.using(model).filter(subsystem_id=subsystem_id).select_related("rc")
    sesQuerySet = APImodels.SubsystemEnzyme.objects.using(model).filter(subsystem_id=subsystem_id).select_related("rc")

    r = APImodels.Reaction.objects.using(model).filter(subsystem=subsystem_id). \
    prefetch_related('modifiers').distinct()

    sms = []; ses = [];
    for m in smsQuerySet:
        sms.append(m.rc)
    for e in sesQuerySet:
        ses.append(e.rc)


    ReactionSerializerClass= componentDBserializerSelector(model, 'reaction', serializer_type='table', api_version=request.version)
    SubsystemSerializerClass = componentDBserializerSelector(model, 'subsystem', serializer_type='lite', api_version=request.version)

    results = {
        'subsystemAnnotations': SubsystemSerializerClass(s, context={'model': model}).data,
        'metabolites': APIrcSerializer.ReactionComponentLiteSerializer(sms, many=True, context={'model': model}).data,
        'enzymes': APIrcSerializer.ReactionComponentLiteSerializer(ses, many=True, context={'model': model}).data,
        'reactions': ReactionSerializerClass(r, many=True, context={'model': model}).data
    }

    return JSONResponse(results)


@api_view()
@is_model_valid
def get_subsystems(request, model):
    """
        List all subsystems/pathways/collection of reactions for the given model.
    """
    try:
        subsystems = APImodels.Subsystem.objects.using(model).all().prefetch_related('compartment')
    except APImodels.Subsystem.DoesNotExist:
        return HttpResponse(status=404)

    serializerClass = componentDBserializerSelector(model, 'subsystem', api_version=request.version)
    serializer = serializerClass(subsystems, many=True, context={'model': model})

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_compartments(request, model):
    '''
        List all compartments for the given model.
    '''
    try:
        compartment = APImodels.Compartment.objects.using(model).all()
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    serializer = APIserializer.CompartmentSerializer(compartment, many=True)

    return JSONResponse(serializer.data)


@api_view()
@is_model_valid
def get_compartment(request, model, compartment_name_id, stats_only=False):
    # stats only is true when this function is called form the compartment page
    # false when called using the swagger api
    """
        For a given compartment name, get all containing metabolites, enzymes, reactions and subsystems.
    """
    try:
        compartment = APImodels.Compartment.objects.using(model).get(Q(name_id__iexact=compartment_name_id) | Q(name__iexact=compartment_name_id))
        compartment_id = compartment.id
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    try:
        c = APImodels.Compartment.objects.using(model).get(id=compartment_id)
    except APImodels.Compartment.DoesNotExist:
        return HttpResponse(status=404)

    subsystems = APImodels.SubsystemCompartment.objects.using(model).filter(compartment_id=compartment_id). \
        prefetch_related('subsystem').distinct().values_list('subsystem__name', flat=True)

    if stats_only:
        results = {
            'compartmentAnnotations': APIserializer.CompartmentSerializer(c, context={'model': model}).data,
            'subsystems': subsystems,
        }
    else:
        sms = APImodels.ReactionComponentCompartment.objects.using(model).filter(compartment_id=compartment_id, rc__component_type='m').select_related("rc").values_list('rc_id', flat=True)
        ses = APImodels.ReactionComponentCompartment.objects.using(model).filter(compartment_id=compartment_id, rc__component_type='e').select_related("rc").values_list('rc_id', flat=True)
        reactions = APImodels.ReactionCompartment.objects.using(model).filter(compartment_id=compartment_id).values_list('reaction_id', flat=True)

        results = {
            'compartmentAnnotations': APIserializer.CompartmentSerializer(c, context={'model': model}).data,
            'subsystems': subsystems,
            'metabolites': sms,
            'enzymes': ses,
            'reactions': reactions,
        }
    return JSONResponse(results)


#=========================================================================================================
# For the Models database

@api_view()
def get_models(request):
    """
    List all Genome-scale metabolic models (GEMs) that are available on the GemsExplorer,
    """
    models = APImodels.GEM.objects.all()
    serializer = APIserializer.GEMListSerializer(models, many=True)
    return JSONResponse(serializer.data)


@api_view()
def get_model(request, model_id):
    """
    Return all known information for a given model available on the GemsExplorer, supply its ID (int) or database_name e.g. 'hmr3'
    """

    try: 
        int(model_id)
        is_int = True
    except ValueError:
        is_int = False

    try:
        if is_int:
            model = APImodels.GEM.objects.get(id=model_id)
        else:
            model = APImodels.GEM.objects.get(database_name__iexact=model_id)
    except APImodels.GEM.DoesNotExist:
        return HttpResponse(status=404)

    serializer = APIserializer.GEMSerializer(model)
    return JSONResponse(serializer.data)


@api_view()
def get_gemodels(request):
    """
    List all GEMs that the group have made
    """
    # get models from database

    serializer = APIserializer.GEModelListSerializer(APImodels.GEModel.objects.all(). \
        prefetch_related('gemodelset__reference', 'ref').select_related('gemodelset', 'sample'), many=True)

    return JSONResponse(serializer.data)


@api_view()
def get_gemodel(request, gem_id):
    """
    For a given Genome-scale metabolic model ID or label, pull out everything we know about it.
    """

    try: 
        int(gem_id)
        is_int = True
    except ValueError:
        is_int = False

    if is_int:
         model = APImodels.GEModel.objects.filter(id=gem_id). \
         prefetch_related('files', 'ref')
    else:
         if gem_id == "HMR2":
             gem_id = "HMR 2.0" # TODO fix . in url
         model = APImodels.GEModel.objects.filter(label__iexact=gem_id). \
             prefetch_related('files', 'ref')

    if not model:
        return HttpResponse(status=404)

    serializer = APIserializer.GEModelSerializer(model[0])
    return JSONResponse(serializer.data)
