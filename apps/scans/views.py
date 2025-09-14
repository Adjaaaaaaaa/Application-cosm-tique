"""
Views for product scanning functionality.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Scan
from .services import ProductAnalysisService, IntelligentCosmeticScorer
from common.mixins import MessageMixin, ContextEnhancerMixin, DemoModeMixin
from common.premium_utils import (
    ResponseBuilder,
    ErrorHandler
)

import logging
logger = logging.getLogger(__name__)


class DemoScanView(DemoModeMixin, View):
    """
    Public demo scan view with conditional demo mode display.
    
    Cette vue affiche le Mode Démonstration uniquement pour les utilisateurs non connectés
    afin de simplifier l'accès au scan pour les clients authentifiés.
    """
    
    template_name = 'scans/demo_scan.html'
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests for demo scan."""
        return self._process_scan_request(request)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests for demo scan."""
        return self._process_scan_request(request)
    
    def _process_scan_request(self, request):
        """
        Process scan request and return response.
        
        Cette méthode traite les requêtes de scan et gère l'affichage conditionnel
        du Mode Démonstration selon le statut d'authentification de l'utilisateur.
        """
        # Initialiser le contexte avec les données du mode démo
        context = self.get_demo_mode_context()
        
        # Si un code-barres est dans la requête GET ou POST, essayer de trouver le produit
        barcode = request.GET.get('barcode') or request.POST.get('barcode')
        if barcode:
            context.update(self._process_barcode_scan(barcode, request))
        
        return render(request, self.template_name, context)
    
    def _process_barcode_scan(self, barcode: str, request) -> dict:
        """
        Process barcode scan and return product data following the complete workflow.
        
        Args:
            barcode: The barcode to scan
            request: The HTTP request object
            
        Returns:
            dict: Product data and analysis results
        """
        # Use ProductAnalysisService for complete workflow implementation
        analysis_service = ProductAnalysisService()
        analysis_result = analysis_service.analyze_product(barcode)

        product_data = analysis_result['product']
        context = {'product': product_data}
        context['found_in_scan'] = True

        # Enhanced analysis with H-codes categorization
        # Always prefer cleaned INCI list when available to avoid grouped evaluation
        ingredients = []
        if product_data.get('ingredients_list'):
            # Use cleaned list provided by OpenBeautyService/Azure OpenAI
            ingredients = [ing for ing in product_data['ingredients_list'] if isinstance(ing, str) and ing.strip()]
        elif product_data.get('ingredients_text'):
            # Fallback: clean raw text via IngredientCleanerService before analysis
            try:
                from backend.services.ingredient_cleaner_service import IngredientCleanerService
                cleaner = IngredientCleanerService()
                cleaned = cleaner.clean_ingredients_list(product_data['ingredients_text'], product_data.get('name', ''))
                ingredients = cleaned.get('cleaned_ingredients', [])
            except Exception:
                # Final fallback: basic splitting
                ingredients = [ing.strip() for ing in product_data['ingredients_text'].replace(';', ',').replace('.', ',').split(',') if ing.strip()]

        if ingredients:
            # Use IntelligentCosmeticScorer for H-codes analysis
            scorer = IntelligentCosmeticScorer()
            enhanced_analysis = scorer.calculate_product_score(ingredients)
            
            # Utiliser le score de l'analyse améliorée pour la cohérence
            final_score = enhanced_analysis.get('score_produit')
            final_risk_level = enhanced_analysis.get('notation', analysis_result.get('risk_level', 'Unknown'))

            context.update({
                'enhanced_analysis': enhanced_analysis,
                'ingredients_analysis': analysis_result.get('ingredients_analysis', {}),
                'safety_score': final_score,  # Score final cohérent
                'risk_level': final_risk_level,  # Notation finale cohérente
                'data_sources': analysis_result.get('data_sources', []),
                'analysis_available': True
            })
        else:
            # Check if ingredients were generated by Azure OpenAI
            if product_data.get('source') == 'azure_llm_generated' and product_data.get('ingredients_list'):
                # Azure OpenAI generated ingredients - analyze them
                scorer = IntelligentCosmeticScorer()
                enhanced_analysis = scorer.calculate_product_score(product_data['ingredients_list'])
                
                context.update({
                    'enhanced_analysis': enhanced_analysis,
                    'ingredients_analysis': analysis_result.get('ingredients_analysis', {}),
                    'safety_score': enhanced_analysis.get('score_produit'),
                    'risk_level': enhanced_analysis.get('niveau_risque', 'Unknown'),
                    'data_sources': analysis_result.get('data_sources', []),
                    'analysis_available': True
                })
            else:
                # No ingredients available at all
                context.update({
                    'ingredients_analysis': analysis_result.get('ingredients_analysis', {}),
                    'safety_score': None,  # No score when no ingredients
                    'risk_level': 'Unknown',
                    'data_sources': analysis_result.get('data_sources', []),
                    'analysis_available': False
                })
        
        # Sauvegarder le scan si l'utilisateur est connecté
        if request.user.is_authenticated:
            self._save_scan_for_authenticated_user(request, barcode, product_data, context)
        
        return context
    
    def _save_scan_for_authenticated_user(self, request, barcode: str, product_data: dict, context: dict):
        """
        Sauvegarde le scan pour un utilisateur connecté.
        
        Args:
            request: The HTTP request object
            barcode: The scanned barcode
            product_data: Product information
            context: Analysis context with enhanced results
        """
        try:
            # Créer un nouveau scan
            scan = Scan.objects.create(
                user=request.user,
                scan_type='barcode',
                barcode=barcode,
                product_name=product_data.get('name', ''),
                product_brand=product_data.get('brand', ''),
                product_description=product_data.get('description', ''),
                product_ingredients_text=product_data.get('ingredients_text', ''),
                product_score=context.get('safety_score'),  # Utiliser le score de l'analyse améliorée
                product_risk_level=context.get('risk_level', 'Unknown'),
                analysis_available=context.get('analysis_available', False)
            )
            
            # Message de sauvegarde supprimé pour une interface plus épurée
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la sauvegarde: {str(e)}')
    
    def _analyze_product_ingredients(self, product) -> dict:
        """
        Analyze product ingredients and return analysis data.
        
        This method is kept for backward compatibility but is no longer used
        as analysis is now handled by ProductAnalysisService.
        
        Args:
            product: The product data to analyze
            
        Returns:
            dict: Basic analysis results
        """
        try:
            # Fallback analysis if ProductAnalysisService is not available
            ingredients = product.get('ingredients_text', '').split(', ') if product.get('ingredients_text') else []
            
            return {
                'ingredients': ingredients,
                'total_ingredients': len(ingredients),
                'analysis_available': bool(ingredients)
            }
            
        except Exception as e:
            return {'analysis_error': f'Erreur d\'analyse: {str(e)}'}


# Alias pour la compatibilité avec les URLs existantes
def demo_scan_view(request):
    """Alias function for backward compatibility."""
    view = DemoScanView()
    view.request = request
    return view._process_scan_request(request)


class ScanListView(LoginRequiredMixin, ListView):
    """List all scans for the current user."""
    model = Scan
    template_name = 'scans/scan_list.html'
    context_object_name = 'scans'
    paginate_by = 10
    
    def get_queryset(self):
        """Filter scans by current user."""
        return Scan.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Get context data for scan list."""
        return super().get_context_data(**kwargs)


class ScanDetailView(LoginRequiredMixin, ContextEnhancerMixin, DetailView):
    """Show detailed information about a scan."""
    model = Scan
    template_name = 'scans/scan_detail.html'
    context_object_name = 'scan'
    
    def get_queryset(self):
        """Filter scans by current user."""
        return Scan.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        """Add additional context for scan analysis."""
        context = super().get_context_data(**kwargs)
        scan = self.object
        
        if scan.product_name and scan.product_ingredients_text:
            # Simplified analysis without external services
            try:
                ingredients = scan.product_ingredients_text.split(', ') if scan.product_ingredients_text else []
                context['ingredients'] = ingredients
                context['total_ingredients'] = len(ingredients)
                context['analysis_available'] = bool(ingredients)
                
            except Exception as e:
                context['score_error'] = f'Erreur d\'analyse: {str(e)}'
        
        return context


class ScanCreateView(LoginRequiredMixin, ContextEnhancerMixin, CreateView):
    """Create a new scan."""
    model = Scan
    template_name = 'scans/scan_form.html'
    fields = ['scan_type', 'barcode', 'image', 'notes']
    
    def get_context_data(self, **kwargs):
        """Add product data to context if available."""
        context = super().get_context_data(**kwargs)
        
        # Si un code-barres est dans la requête GET, essayer de trouver le produit
        barcode = self.request.GET.get('barcode') or self.request.POST.get('barcode')
        if barcode:
            # Use ProductAnalysisService to get real product data
            analysis_service = ProductAnalysisService()
            analysis_result = analysis_service.analyze_product(barcode)
            
            context['product'] = analysis_result['product']
            context['found_in_scan'] = True
            context['ingredients_analysis'] = analysis_result.get('ingredients_analysis', {})
            context['safety_score'] = analysis_result.get('safety_score')
            context['risk_level'] = analysis_result.get('risk_level')
            context['data_sources'] = analysis_result.get('data_sources', [])
            context['analysis_available'] = analysis_result.get('analysis_available', False)
        
        return context
    
    def form_valid(self, form):
        """Set the user and handle product lookup."""
        form.instance.user = self.request.user
        
        # Si un code-barres est fourni, essayer de trouver le produit
        if form.instance.barcode:
            # Use ProductAnalysisService to get real product data
            analysis_service = ProductAnalysisService()
            analysis_result = analysis_service.analyze_product(form.instance.barcode)
            
            product_data = analysis_result['product']
            
            # Store product information directly in the scan
            form.instance.product_name = product_data.get('name', '')
            form.instance.product_brand = product_data.get('brand', '')
            form.instance.product_description = product_data.get('description', '')
            form.instance.product_ingredients_text = product_data.get('ingredients_text', '')
            form.instance.product_score = analysis_result.get('safety_score')
            form.instance.product_risk_level = analysis_result.get('risk_level', 'Unknown')
            form.instance.analysis_available = analysis_result.get('analysis_available', False)
            
            # Messages de confirmation supprimés pour une interface plus épurée
        
        # Message de succès simplifié
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to scan detail after creation."""
        return reverse_lazy('scans:scan_detail', kwargs={'pk': self.object.pk})


@login_required
def scan_dashboard(request):
    """Dashboard showing scan statistics and recent scans."""
    user_scans = Scan.objects.filter(user=request.user)
    
    context = {
        'total_scans': user_scans.count(),
        'recent_scans': user_scans[:5],
        'scan_types': {
            'barcode': user_scans.filter(scan_type='barcode').count(),
            'image': user_scans.filter(scan_type='image').count(),
            'manual': user_scans.filter(scan_type='manual').count(),
        },
        'products_scanned': user_scans.filter(product_name__isnull=False).exclude(product_name='').count(),
    }
    
    return render(request, 'scans/dashboard.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class ScanAPIView(LoginRequiredMixin, MessageMixin, View):
    """API view for creating scans via AJAX."""
    
    def post(self, request, *args, **kwargs):
        """Handle scan creation via AJAX."""
        try:
            scan_type = request.POST.get('scan_type')
            barcode = request.POST.get('barcode')
            notes = request.POST.get('notes', '')
            
            scan = Scan.objects.create(
                user=request.user,
                scan_type=scan_type,
                barcode=barcode,
                notes=notes
            )
            
            # Essayer de trouver le produit
            if barcode:
                # Use ProductAnalysisService to get real product data
                analysis_service = ProductAnalysisService()
                analysis_result = analysis_service.analyze_product(barcode)
                
                product_data = analysis_result['product']
                
                # Store product information directly in the scan
                scan.product_name = product_data.get('name', '')
                scan.product_brand = product_data.get('brand', '')
                scan.product_description = product_data.get('description', '')
                scan.product_ingredients_text = product_data.get('ingredients_text', '')
                scan.product_score = analysis_result.get('safety_score')
                scan.product_risk_level = analysis_result.get('risk_level', 'Unknown')
                scan.analysis_available = analysis_result.get('analysis_available', False)
                scan.save()
                
                response_data = {
                    'scan_id': scan.id,
                    'product_name': scan.product_name,
                    'safety_score': analysis_result.get('safety_score'),
                    'risk_level': analysis_result.get('risk_level'),
                    'data_sources': analysis_result.get('data_sources', [])
                }
                
                # Messages de confirmation supprimés pour une interface plus épurée
                return JsonResponse(ResponseBuilder.success_response(response_data, ''))
            
            return JsonResponse(ResponseBuilder.success_response({
                'scan_id': scan.id
            }, ''))
            
        except Exception as e:
            error_message = ErrorHandler.handle_product_analysis_error(e)
            return JsonResponse(ResponseBuilder.error_response(error_message))


@login_required
def scan_analysis(request, scan_id):
    """Show detailed analysis of a scan."""
    scan = get_object_or_404(Scan, id=scan_id, user=request.user)
    
    context = {
        'scan': scan,
        'analysis_data': {}
    }
    
    if scan.product_name and scan.product_ingredients_text:
        try:
            ingredients = scan.product_ingredients_text.split(', ') if scan.product_ingredients_text else []
            
            # Use IntelligentCosmeticScorer for enhanced analysis with H-codes
            from .services import IntelligentCosmeticScorer
            scorer = IntelligentCosmeticScorer()
            
            # Analyze ingredients to get H-codes
            enhanced_analysis = scorer.calculate_product_score(ingredients)
            h_codes_categories = enhanced_analysis.get('categories_h_codes', {})
            
            context['analysis_data'] = {
                'total_ingredients': len(ingredients),
                'low_risk': 0,
                'medium_risk': 0,
                'high_risk': 0,
                'ingredients': ingredients,
                'risk_distribution': {},
                'analysis_available': bool(ingredients),
                'h_codes_categories': h_codes_categories,
                'enhanced_analysis': enhanced_analysis
            }
        except Exception as e:
            context['analysis_error'] = f'Erreur d\'analyse: {str(e)}'
    
    return render(request, 'scans/scan_analysis.html', context)


@login_required
def delete_scan(request, scan_id):
    """Delete a scan from user's history."""
    scan = get_object_or_404(Scan, id=scan_id, user=request.user)
    
    if request.method == 'POST':
        try:
            product_name = scan.product_name or 'Produit inconnu'
            scan.delete()
            messages.success(request, f'Le scan du produit "{product_name}" a été supprimé de votre historique.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression: {str(e)}')
    
    return redirect('scans:scan_list')


class ScanDetailView(LoginRequiredMixin, DetailView):
    """Display scan details."""
    model = Scan
    template_name = 'scans/scan_detail.html'
    
    def get_context_data(self, **kwargs):
        """Add analysis data to context."""
        context = super().get_context_data(**kwargs)
        
        scan = self.object
        
        if scan.product_name and scan.product_ingredients_text:
            # Simplified analysis without external services
            try:
                ingredients = scan.product_ingredients_text.split(', ') if scan.product_ingredients_text else []
                context['ingredients'] = ingredients
                context['total_ingredients'] = len(ingredients)
                context['analysis_available'] = bool(ingredients)
            except Exception as e:
                context['score_error'] = f'Erreur d\'analyse: {str(e)}'
        
        return context


class ScanCreateView(LoginRequiredMixin, ContextEnhancerMixin, CreateView):
    """Create a new scan."""
    model = Scan
    template_name = 'scans/scan_form.html'
    fields = ['scan_type', 'barcode', 'image', 'notes']
    
    def get_context_data(self, **kwargs):
        """Add product data to context if available."""
        context = super().get_context_data(**kwargs)
        
        # Si un code-barres est dans la requête GET, essayer de trouver le produit
        barcode = self.request.GET.get('barcode') or self.request.POST.get('barcode')
        if barcode:
            # Use ProductAnalysisService to get real product data
            analysis_service = ProductAnalysisService()
            analysis_result = analysis_service.analyze_product(barcode)
            
            context['product'] = analysis_result['product']
            context['found_in_scan'] = True
            context['ingredients_analysis'] = analysis_result.get('ingredients_analysis', {})
            context['safety_score'] = analysis_result.get('safety_score')
            context['risk_level'] = analysis_result.get('risk_level')
            context['data_sources'] = analysis_result.get('data_sources', [])
            context['analysis_available'] = analysis_result.get('analysis_available', False)
        
        return context
    
    def form_valid(self, form):
        """Set the user and handle product lookup."""
        form.instance.user = self.request.user
        
        # Si un code-barres est fourni, essayer de trouver le produit
        if form.instance.barcode:
            # Use ProductAnalysisService to get real product data
            analysis_service = ProductAnalysisService()
            analysis_result = analysis_service.analyze_product(form.instance.barcode)
            
            product_data = analysis_result['product']
            
            # Store product information directly in the scan
            form.instance.product_name = product_data.get('name', '')
            form.instance.product_brand = product_data.get('brand', '')
            form.instance.product_description = product_data.get('description', '')
            form.instance.product_ingredients_text = product_data.get('ingredients_text', '')
            form.instance.product_score = analysis_result.get('safety_score')
            form.instance.product_risk_level = analysis_result.get('risk_level', 'Unknown')
            form.instance.analysis_available = analysis_result.get('analysis_available', False)
            
            # Messages de confirmation supprimés pour une interface plus épurée
        
        # Message de succès simplifié
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to scan detail after creation."""
        return reverse_lazy('scans:scan_detail', kwargs={'pk': self.object.pk})





@login_required

def scan_dashboard(request):

    """Dashboard showing scan statistics and recent scans."""

    user_scans = Scan.objects.filter(user=request.user)

    

    context = {

        'total_scans': user_scans.count(),

        'recent_scans': user_scans[:5],

        'scan_types': {

            'barcode': user_scans.filter(scan_type='barcode').count(),

            'image': user_scans.filter(scan_type='image').count(),

            'manual': user_scans.filter(scan_type='manual').count(),

        },

        'products_scanned': user_scans.filter(product_name__isnull=False).exclude(product_name='').count(),

    }

    

    return render(request, 'scans/dashboard.html', context)





@method_decorator(csrf_exempt, name='dispatch')

class ScanAPIView(LoginRequiredMixin, MessageMixin, View):

    """API view for creating scans via AJAX."""

    

    def post(self, request, *args, **kwargs):

        """Handle scan creation via AJAX."""

        try:

            scan_type = request.POST.get('scan_type')

            barcode = request.POST.get('barcode')

            notes = request.POST.get('notes', '')

            

            scan = Scan.objects.create(

                user=request.user,

                scan_type=scan_type,

                barcode=barcode,

                notes=notes

            )

            

            # Essayer de trouver le produit

            if barcode:

                # Use ProductAnalysisService to get real product data with cache optimization

                analysis_service = ProductAnalysisService()

                analysis_result = analysis_service.analyze_product(barcode, user_id=request.user.id)

                

                product_data = analysis_result['product']

                

                # Store product information directly in the scan

                scan.product_name = product_data.get('name', '')

                scan.product_brand = product_data.get('brand', '')

                scan.product_description = product_data.get('description', '')

                scan.product_ingredients_text = product_data.get('ingredients_text', '')

                scan.product_score = analysis_result.get('safety_score')
                scan.product_risk_level = analysis_result.get('risk_level', 'Unknown')
                scan.analysis_available = analysis_result.get('analysis_available', False)
                scan.save()

                

                response_data = {

                    'scan_id': scan.id,

                    'product_name': scan.product_name,

                    'safety_score': analysis_result.get('safety_score'),

                    'risk_level': analysis_result.get('risk_level'),

                    'data_sources': analysis_result.get('data_sources', [])

                }

                

                if analysis_result.get('error'):

                    return JsonResponse(ResponseBuilder.success_response(

                        response_data, 

                        f'Scan créé avec produit trouvé mais {analysis_result["error"]}'

                    ))

                else:

                    return JsonResponse(ResponseBuilder.success_response(

                        response_data, 

                        'Scan créé avec produit trouvé'

                    ))

            

            return JsonResponse(ResponseBuilder.success_response({

                'scan_id': scan.id

            }, 'Scan créé avec succès'))

            

        except Exception as e:

            error_message = ErrorHandler.handle_product_analysis_error(e)

            return JsonResponse(ResponseBuilder.error_response(error_message))





@login_required

def scan_analysis(request, scan_id):

    """Show detailed analysis of a scan."""

    scan = get_object_or_404(Scan, id=scan_id, user=request.user)

    

    context = {

        'scan': scan,

        'analysis_data': {}

    }

    

    if scan.product_name and scan.product_ingredients_text:

        try:

            ingredients = scan.product_ingredients_text.split(', ') if scan.product_ingredients_text else []

            
            # Use IntelligentCosmeticScorer for enhanced analysis with H-codes
            from .services import IntelligentCosmeticScorer
            scorer = IntelligentCosmeticScorer()
            
            # Analyze ingredients to get H-codes
            enhanced_analysis = scorer.calculate_product_score(ingredients)
            h_codes_categories = enhanced_analysis.get('categories_h_codes', {})
            

            context['analysis_data'] = {

                'total_ingredients': len(ingredients),

                'low_risk': 0,

                'medium_risk': 0,

                'high_risk': 0,

                'ingredients': ingredients,

                'risk_distribution': {},

                'analysis_available': bool(ingredients),
                'h_codes_categories': h_codes_categories,
                'enhanced_analysis': enhanced_analysis
            }

        except Exception as e:

            context['analysis_error'] = f'Erreur d\'analyse: {str(e)}'

    

    return render(request, 'scans/scan_analysis.html', context)





@login_required

def delete_scan(request, scan_id):

    """Delete a scan from user's history."""

    scan = get_object_or_404(Scan, id=scan_id, user=request.user)

    

    if request.method == 'POST':

        try:

            product_name = scan.product_name or 'Produit inconnu'

            scan.delete()

            messages.success(request, f'Le scan du produit "{product_name}" a été supprimé de votre historique.')

        except Exception as e:

            messages.error(request, f'Erreur lors de la suppression: {str(e)}')

    

    return redirect('scans:scan_list')



def about_view(request):
    """
    Vue pour afficher la page "À propos de nous"
    """
    context = {
        'page_title': 'À propos de nous',
        'demo_title': 'À propos de BeautyScan',
        'demo_subtitle': 'Découvrez notre histoire et nos fondatrices',
    }
    return render(request, 'about.html', context)


