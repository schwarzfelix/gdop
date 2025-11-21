"""Correlation analysis for GDOP vs Position Error - Console output only.

This module provides correlation statistics printed to the console rather than as a plot.
Useful for quick statistical analysis without opening a window.
"""

from scipy import stats
import numpy as np


class GDOPCorrelationAnalysis:
    """Calculate and display correlation statistics between GDOP and Position Error.
    
    Computes both Pearson (linear) and Spearman (monotonic) correlation coefficients
    with their p-values and displays them in the console.
    
    Expected usage:
      analysis = GDOPCorrelationAnalysis(scenarios)
      analysis.run_analysis()
    """

    def __init__(self, scenarios):
        self.scenarios = scenarios

    def _format_pvalue(self, p_value):
        """Format p-value nicely, handling very small values."""
        if p_value == 0.0:
            return "< 1e-300"
        elif p_value < 1e-10:
            return f"{p_value:.3e}"
        else:
            return f"{p_value:.6f}"

    def run_analysis(self):
        """Collect data and print correlation analysis to console."""
        gdop_values = []
        pos_errors = []
        scenario_names = []
        scenario_metadata = []

        print("\n" + "="*80)
        print("GDOP vs POSITION ERROR - CORRELATION ANALYSIS")
        print("="*80 + "\n")

        # Collect data from scenarios
        for s in self.scenarios:
            try:
                scenario_name = getattr(s, 'name', str(s))
                tags = s.get_tag_list()
                if tags and len(tags) > 0:
                    tag = tags[0]
                    try:
                        pos_error = tag.position_error()
                        if pos_error is None:
                            continue
                    except Exception:
                        continue

                    try:
                        tag_truth_gdop = s.get_tag_truth_gdop()
                    except Exception:
                        continue

                    gdop_values.append(float(tag_truth_gdop))
                    pos_errors.append(float(pos_error))
                    scenario_names.append(scenario_name)
                    
                    # Collect metadata about methods used
                    metadata = {
                        'name': scenario_name,
                        'aggregation_method': getattr(s, 'aggregation_method', 'unknown'),
                        'trilateration_method': getattr(s, 'trilateration_method', 'classical'),
                    }
                    scenario_metadata.append(metadata)
                    
            except Exception:
                # Skip scenarios that raise exceptions during processing
                continue

        if len(gdop_values) < 2:
            print("ERROR: Not enough data points for correlation analysis.")
            print(f"       Found {len(gdop_values)} scenario(s), need at least 2.\n")
            print("="*80 + "\n")
            return

        # Convert to numpy arrays
        gdop_arr = np.array(gdop_values)
        pos_err_arr = np.array(pos_errors)

        # Calculate Pearson correlation (linear relationship)
        pearson_r, pearson_p = stats.pearsonr(gdop_arr, pos_err_arr)

        # Calculate Spearman correlation (monotonic relationship, more robust)
        spearman_r, spearman_p = stats.spearmanr(gdop_arr, pos_err_arr)

        # Linear regression for additional context
        slope, intercept, r_value, _, std_err = stats.linregress(gdop_arr, pos_err_arr)

        # Print summary statistics
        print(f"Sample Size: {len(gdop_values)} scenarios\n")
        
        # Show method distribution
        print("="*80)
        print("METHODS USED")
        print("="*80 + "\n")
        
        agg_methods = {}
        trilat_methods = {}
        
        for metadata in scenario_metadata:
            agg = metadata['aggregation_method']
            trilat = metadata['trilateration_method']
            
            agg_methods[agg] = agg_methods.get(agg, 0) + 1
            trilat_methods[trilat] = trilat_methods.get(trilat, 0) + 1
        
        print("Aggregation Methods:")
        for method, count in sorted(agg_methods.items()):
            percentage = count / len(gdop_values) * 100
            print(f"  • {method}: {count} scenarios ({percentage:.1f}%)")
        
        print("\nTrilateration Methods:")
        for method, count in sorted(trilat_methods.items()):
            percentage = count / len(gdop_values) * 100
            print(f"  • {method}: {count} scenarios ({percentage:.1f}%)")
        
        print("\n" + "="*80)
        print("DESCRIPTIVE STATISTICS")
        print("="*80 + "\n")
        
        print("GDOP Statistics:")
        print(f"  Mean:   {np.mean(gdop_arr):.4f}")
        print(f"  Median: {np.median(gdop_arr):.4f}")
        print(f"  Std:    {np.std(gdop_arr):.4f}")
        print(f"  Range:  [{np.min(gdop_arr):.4f}, {np.max(gdop_arr):.4f}]\n")

        print("Position Error Statistics:")
        print(f"  Mean:   {np.mean(pos_err_arr):.4f} m")
        print(f"  Median: {np.median(pos_err_arr):.4f} m")
        print(f"  Std:    {np.std(pos_err_arr):.4f} m")
        print(f"  Range:  [{np.min(pos_err_arr):.4f}, {np.max(pos_err_arr):.4f}] m\n")

        print("-"*80)
        print("CORRELATION COEFFICIENTS")
        print("-"*80 + "\n")

        # Pearson correlation
        print("PEARSON CORRELATION (measures linear relationship):")
        print(f"  r = {pearson_r:+.6f}")
        
        # Format p-value nicely, handling very small values
        if pearson_p == 0.0:
            print(f"  p-value < 1e-300 (effectively zero)", end="")
        elif pearson_p < 1e-10:
            print(f"  p-value = {pearson_p:.3e}", end="")
        else:
            print(f"  p-value = {pearson_p:.6f}", end="")
            
        if pearson_p < 0.001:
            print("  *** (highly significant)")
        elif pearson_p < 0.01:
            print("  ** (very significant)")
        elif pearson_p < 0.05:
            print("  * (significant)")
        else:
            print("  (not significant)")
        
        print(f"  R² = {r_value**2:.6f} ({r_value**2 * 100:.2f}% of variance explained)")
        
        # Interpretation of Pearson r
        abs_r = abs(pearson_r)
        if abs_r < 0.3:
            strength = "WEAK"
        elif abs_r < 0.7:
            strength = "MODERATE"
        else:
            strength = "STRONG"
        
        direction = "positive" if pearson_r > 0 else "negative"
        print(f"  Interpretation: {strength} {direction} linear correlation\n")

        # Spearman correlation
        print("SPEARMAN CORRELATION (measures monotonic relationship, robust to outliers):")
        print(f"  ρ (rho) = {spearman_r:+.6f}")
        
        # Format p-value nicely, handling very small values
        if spearman_p == 0.0:
            print(f"  p-value < 1e-300 (effectively zero)", end="")
        elif spearman_p < 1e-10:
            print(f"  p-value = {spearman_p:.3e}", end="")
        else:
            print(f"  p-value = {spearman_p:.6f}", end="")
            
        if spearman_p < 0.001:
            print("  *** (highly significant)")
        elif spearman_p < 0.01:
            print("  ** (very significant)")
        elif spearman_p < 0.05:
            print("  * (significant)")
        else:
            print("  (not significant)")
        
        # Interpretation of Spearman rho
        abs_rho = abs(spearman_r)
        if abs_rho < 0.3:
            strength = "WEAK"
        elif abs_rho < 0.7:
            strength = "MODERATE"
        else:
            strength = "STRONG"
        
        direction = "positive" if spearman_r > 0 else "negative"
        print(f"  Interpretation: {strength} {direction} monotonic correlation\n")

        # Linear regression equation
        print("-"*80)
        print("LINEAR REGRESSION")
        print("-"*80 + "\n")
        print(f"  Position Error = {slope:.6f} × GDOP + {intercept:.6f}")
        print(f"  Standard Error: {std_err:.6f}\n")

        # Comparison and recommendation
        print("-"*80)
        print("COMPARISON & RECOMMENDATION")
        print("-"*80 + "\n")
        
        if abs(pearson_r - spearman_r) < 0.05:
            print("✓ Pearson and Spearman coefficients are very similar.")
            print("  → Linear relationship is a good model.\n")
        elif abs(spearman_r) > abs(pearson_r) + 0.1:
            print("⚠ Spearman coefficient is notably higher than Pearson.")
            print("  → Relationship may be monotonic but non-linear.")
            print("  → Consider checking residual plot for patterns.\n")
        else:
            print("ℹ Pearson and Spearman coefficients differ moderately.")
            print("  → Some non-linearity may be present.\n")

        # Overall conclusion
        if pearson_p < 0.05 and abs(pearson_r) > 0.5:
            print("CONCLUSION: GDOP shows a statistically significant and practically")
            print("            meaningful correlation with Position Error.")
            if pearson_r > 0:
                print("            Higher GDOP values tend to correspond to higher position errors.")
        elif pearson_p < 0.05:
            print("CONCLUSION: GDOP shows a statistically significant but weak")
            print("            correlation with Position Error.")
        else:
            print("CONCLUSION: No statistically significant correlation found.")
            print("            GDOP may not be a reliable predictor of Position Error")
            print("            in this dataset.")

        print("\n" + "="*80)
        print("LEGEND:")
        print("  * p < 0.05  (significant)")
        print("  ** p < 0.01  (very significant)")
        print("  *** p < 0.001  (highly significant)")
        print("="*80)
        
        # Method-specific correlation analysis
        if len(agg_methods) > 1 or len(trilat_methods) > 1:
            print("\n" + "="*80)
            print("CORRELATION BY METHOD")
            print("="*80 + "\n")
            
            # Correlation by aggregation method
            if len(agg_methods) > 1:
                print("By Aggregation Method:")
                print("-"*80)
                
                for agg_method in sorted(agg_methods.keys()):
                    if agg_method == 'unknown' or agg_methods[agg_method] < 2:
                        continue
                    
                    # Filter data for this method
                    indices = [i for i, meta in enumerate(scenario_metadata) 
                              if meta['aggregation_method'] == agg_method]
                    
                    method_gdop = [gdop_values[i] for i in indices]
                    method_errors = [pos_errors[i] for i in indices]
                    
                    pearson_r, pearson_p = stats.pearsonr(method_gdop, method_errors)
                    spearman_r, spearman_p = stats.spearmanr(method_gdop, method_errors)
                    
                    print(f"\n  {agg_method} (n={len(indices)}):")
                    print(f"    Pearson:  r = {pearson_r:+.4f}, p = {self._format_pvalue(pearson_p)}")
                    print(f"    Spearman: ρ = {spearman_r:+.4f}, p = {self._format_pvalue(spearman_p)}")
                
                print()
            
            # Correlation by trilateration method
            if len(trilat_methods) > 1:
                print("\nBy Trilateration Method:")
                print("-"*80)
                
                for trilat_method in sorted(trilat_methods.keys()):
                    if trilat_method == 'unknown' or trilat_methods[trilat_method] < 2:
                        continue
                    
                    # Filter data for this method
                    indices = [i for i, meta in enumerate(scenario_metadata) 
                              if meta['trilateration_method'] == trilat_method]
                    
                    method_gdop = [gdop_values[i] for i in indices]
                    method_errors = [pos_errors[i] for i in indices]
                    
                    pearson_r, pearson_p = stats.pearsonr(method_gdop, method_errors)
                    spearman_r, spearman_p = stats.spearmanr(method_gdop, method_errors)
                    
                    print(f"\n  {trilat_method} (n={len(indices)}):")
                    print(f"    Pearson:  r = {pearson_r:+.4f}, p = {self._format_pvalue(pearson_p)}")
                    print(f"    Spearman: ρ = {spearman_r:+.4f}, p = {self._format_pvalue(spearman_p)}")
                
                print()
            
            print("="*80)

        print()

        # Return the statistics for programmatic access if needed
        return {
            'n_samples': len(gdop_values),
            'pearson_r': pearson_r,
            'pearson_p': pearson_p,
            'spearman_r': spearman_r,
            'spearman_p': spearman_p,
            'r_squared': r_value**2,
            'slope': slope,
            'intercept': intercept,
            'std_err': std_err
        }
