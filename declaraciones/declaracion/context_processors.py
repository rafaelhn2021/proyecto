from .models import  sitio_personalizacion

def g_custom_css(request):
	try:
		p = sitio_personalizacion.objects.all()[0]
		
		bg_color = p.bg_color
		font_color_primary = p.font_color_primary
		color_primary = p.color_primary
		color_secondary = p.color_secondary
		color_success = p.color_success
		color_info = p.color_info
		color_warning = p.color_warning
		color_danger = p.color_danger
		color_light = p.color_light
		color_dark = p.color_dark
		color_footer_bg = p.color_footer_bg

		custom = { 
			"bg_color" : bg_color,
			"font_color_primary" : font_color_primary,
			"color_primary" : color_primary,
			"color_secondary" : color_secondary,
			"color_success": color_success,
			"color_info" : color_info,
			"color_warning" :color_warning,
			"color_danger" : color_danger,
			"color_light" : color_light,
			"color_dark": color_dark,
			"color_footer_bg" : color_footer_bg
		}
	except Exception as e:
		print("CUSTOM_CSS_ERROR" + e)
		custom = {
			"bg_color":"white",
			"font_color_primary":"#061d26",
			"color_primary":"#96f164",
			"color_secondary":"#727176",
			"color_success":"#5dffff",
			"color_info":"#96f164",
			"color_warning":"#727176",
			"color_danger":"#5d5d5e",
			"color_light":"#015F78",
			"color_dark":"#727176",
			"color_footer_bg":"#015F78",
		}


	custom_css = { "custom_css": custom }

	return custom_css